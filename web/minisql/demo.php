<?php
// import settings
require_once 'include/db_config.php';
require_once 'include/template_engine.php';

// create connection
$db = new mysqli(DB_HOST, DB_PORT)
or die("Connection to db failed: " . $db->connect_error);
?>