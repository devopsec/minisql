<?php
/* DEBUG:
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
*/
error_reporting(E_ALL);

/* forgo auth for this demonstration */
session_start();
$_SESSION['name'] = "Admin";
$_SESSION['id'] = 1;

// list of tables to demo
const DEMO_TABLES = [
        'address',
        'agent',
        'auto_insurance_policy',
        'beneficiaries',
        'customer',
        'home_insurance_policy',
        'insurance_company',
        'life_insurance_policy',
        'premium',
        'sales',
        'vehicle'
];
?>

<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Databases Demo</title>
</head>
<body>

<h1>Pick A Table</h1>

<section>
    <?php
    foreach (DEMO_TABLES as $table) {
        echo '
      <div>
        <a href="/mysql/views/tables.php?table=' . $table . '">' . ucwords($table) . ' Demo</a>
      </div>';
    }
    ?>
</section>

</body>
</html>
