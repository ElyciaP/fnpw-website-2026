<?php
/**
 * The import package: upload, storage in uploads/fnpw-migrate/ and reading.
 *
 * @package fnpw-migrate
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Private folder for packages. Returns the path, or WP_Error.
 */
function fnpw_migrate_dir() {
	$uploads = wp_upload_dir();
	if ( ! empty( $uploads['error'] ) ) {
		return new WP_Error( 'fnpw_migrate_uploads', $uploads['error'] );
	}
	$dir = trailingslashit( $uploads['basedir'] ) . 'fnpw-migrate';
	if ( ! wp_mkdir_p( $dir ) ) {
		return new WP_Error( 'fnpw_migrate_dir', 'Could not create ' . $dir );
	}
	// Packages are not for the public: block listing and direct reads where the server honours it.
	if ( ! file_exists( $dir . '/index.php' ) ) {
		file_put_contents( $dir . '/index.php', "<?php\n// Silence is golden.\n" ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	}
	if ( ! file_exists( $dir . '/.htaccess' ) ) {
		file_put_contents( $dir . '/.htaccess', "Require all denied\nDeny from all\n" ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	}
	return $dir;
}

/**
 * Take an uploaded .json or .zip (holding package.json), check it and store it.
 *
 * @param array $file One entry of $_FILES.
 * @return array|WP_Error Package info as stored in the fnpw_migrate_package option.
 */
function fnpw_migrate_store_upload( $file ) {
	if ( empty( $file['tmp_name'] ) || ! is_uploaded_file( $file['tmp_name'] ) ) {
		$code = isset( $file['error'] ) ? (int) $file['error'] : 0;
		return new WP_Error( 'fnpw_migrate_upload', $code ? 'Upload failed (PHP upload error ' . $code . '; the file may be larger than upload_max_filesize).' : 'No file was uploaded.' );
	}
	$name = sanitize_file_name( (string) $file['name'] );
	$ext  = strtolower( pathinfo( $name, PATHINFO_EXTENSION ) );
	if ( 'zip' === $ext ) {
		if ( ! class_exists( 'ZipArchive' ) ) {
			return new WP_Error( 'fnpw_migrate_zip', 'This server cannot open zip files. Upload package.json instead.' );
		}
		$zip = new ZipArchive();
		if ( true !== $zip->open( $file['tmp_name'] ) ) {
			return new WP_Error( 'fnpw_migrate_zip', 'The zip file could not be opened.' );
		}
		$json = false;
		for ( $i = 0; $i < $zip->numFiles; $i++ ) { // phpcs:ignore WordPress.NamingConventions.ValidVariableName
			if ( 'package.json' === basename( (string) $zip->getNameIndex( $i ) ) ) {
				$json = $zip->getFromIndex( $i );
				break;
			}
		}
		$zip->close();
		if ( false === $json ) {
			return new WP_Error( 'fnpw_migrate_zip', 'The zip file holds no package.json.' );
		}
	} elseif ( 'json' === $ext ) {
		$json = file_get_contents( $file['tmp_name'] ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	} else {
		return new WP_Error( 'fnpw_migrate_type', 'Upload a .json package or a .zip that holds package.json.' );
	}
	$data = json_decode( (string) $json, true );
	if ( ! is_array( $data ) || empty( $data['format'] ) || 0 !== strpos( (string) $data['format'], 'fnpw-migrate/' ) || ! isset( $data['items'] ) || ! is_array( $data['items'] ) ) {
		return new WP_Error( 'fnpw_migrate_format', 'That file is not an FNPW import package (' . ( json_last_error() ? json_last_error_msg() : 'no "format" and "items"' ) . ').' );
	}
	$dir = fnpw_migrate_dir();
	if ( is_wp_error( $dir ) ) {
		return $dir;
	}
	$hash   = substr( sha1( (string) $json ), 0, 16 );
	$target = $dir . '/package-' . $hash . '.json';
	if ( false === file_put_contents( $target, $json ) ) { // phpcs:ignore WordPress.WP.AlternativeFunctions
		return new WP_Error( 'fnpw_migrate_write', 'Could not write the package to ' . $dir );
	}
	$info = array(
		'file'      => basename( $target ),
		'name'      => $name,
		'hash'      => $hash,
		'uploaded'  => time(),
		'items'     => count( $data['items'] ),
		'media'     => isset( $data['media'] ) && is_array( $data['media'] ) ? count( $data['media'] ) : 0,
		'generated' => isset( $data['generated'] ) ? (string) $data['generated'] : '',
		'base'      => isset( $data['media_base'] ) ? (string) $data['media_base'] : '',
		'settings'  => ! empty( $data['settings'] ),
	);
	update_option( 'fnpw_migrate_package', $info, false );
	return $info;
}

/**
 * The stored package, decoded, or WP_Error. Cached for the request.
 */
function fnpw_migrate_package() {
	static $cache = null;
	if ( null !== $cache ) {
		return $cache;
	}
	$info = get_option( 'fnpw_migrate_package' );
	$dir  = fnpw_migrate_dir();
	if ( is_wp_error( $dir ) ) {
		return $dir;
	}
	if ( ! is_array( $info ) || empty( $info['file'] ) || ! is_readable( $dir . '/' . basename( $info['file'] ) ) ) {
		return new WP_Error( 'fnpw_migrate_none', 'No package has been uploaded yet.' );
	}
	$data = json_decode( (string) file_get_contents( $dir . '/' . basename( $info['file'] ) ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	if ( ! is_array( $data ) ) {
		return new WP_Error( 'fnpw_migrate_read', 'The stored package could not be read.' );
	}
	$data['items'] = array_values( (array) $data['items'] );
	$data['media'] = isset( $data['media'] ) ? array_values( (array) $data['media'] ) : array();
	$cache         = $data;
	return $cache;
}
