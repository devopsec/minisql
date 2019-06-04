<?php
/* DEBUG:
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
*/
error_reporting(E_ALL);

// import settings
require_once 'include/db_config.php';
require_once 'include/template_engine.php';
require_once 'include/form_body.php';

// create connection
$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT)
or die("Connection to db failed: " . $db->connect_error);

// session settings
session_start();

// set table we are working with

/* DEBUG:
  echo "<script>console.log('|=========== POST ===========|')</script>";
  echo "<script>console.log(" . json_encode($_POST) . ")</script>";
  echo "<script>console.log('|=========== FILES ===========|')</script>";
  echo "<script>console.log(" . json_encode($_FILES) . ")</script>";
*/

// request handler
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (array_key_exists('table', $_GET)) {
        $table = $_GET['table'];
        $_SESSION['table'] = $table;
    }
    else {
        $table = $_SESSION['table'];
    }
}
elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
    /* setup to process post */
    function arrayToMysqlQueryString($arr, $action = 'insert') {
        $query = "";

        if ($action === 'insert') {
            $i = 0;
            foreach ($arr as $var) {
                if ($i !== 0) {
                    $query .= ",";
                }

                if (is_numeric($var)) {
                    $query .= strval($var);
                }
                elseif (is_null($var)) {
                    $query .= "NULL";
                }
                elseif (is_string($var)) {
                    $query .= "'" . $var . "'";
                }
                else {
                    $query .= strval($var);
                }

                $i++;
            }
        }
        elseif ($action === 'update') {
            $i = 0;
            foreach ($arr as $key => $val) {
                if ($i !== 0) {
                    $query .= ",";
                }

                if (is_numeric($val)) {
                    $query .= $key . "=" . strval($val);
                }
                elseif (is_null($val)) {
                    $query .= $key . "=" . "NULL";
                }
                elseif (is_string($val)) {
                    $query .= $key . "=" . "'" . $val . "'";
                }
                else {
                    $query .= $key . "=" . strval($val);
                }

                $i++;
            }
        }

        return $query;
    }

    $table = $_SESSION['table'];

    /* interpret empty strings in fields as NULL string (so db uses defaults) */
    function convertEmpty($var) {
        return ($var === '') ? NULL : $var;
    }

    $_POST['field'] = array_map('convertEmpty', $_POST['field']);

    if ($_POST['action'] === 'add') {

        $sql = "INSERT INTO " . $table . " VALUES (" .
                arrayToMysqlQueryString($_POST['field'], 'insert') . ")";

        $res = $db->query($sql);
        if ($res === true) {
            echo "<script>console.log('[OK]: Record created successfully')</script>";
        }
        else {
            echo "<script>console.error('[ERR]: ' + " . json_encode($db->error) . ")</script>";
        }

    }
    elseif ($_POST['action'] === 'edit') {
        if (isset($_POST['row_id'])) {

            $fields = array();
            $i = 0;
            $field_names = explode(',', $_POST['column_names']);
            foreach ($field_names as $name) {
                $fields[$name] = $_POST['field'][$i];
                $i += 1;
            }

            /* were updating so remove the id */;
            unset($fields['id']);

            $sql = "UPDATE " . $table . " SET " .
                    arrayToMysqlQueryString($fields, 'update') .
                    " WHERE id=" . $_POST['row_id'];

            $res = $db->query($sql);
            if ($res === true) {
                echo "<script>console.log('[OK]: Record updated successfully')</script>";
            }
            else {
                echo "<script>console.error('[ERR]: ' + " . json_encode($db->error) . ")</script>";
            }

        }
    }
    elseif ($_POST['action'] === 'delete') {
        if (isset($_POST['row_id'])) {

            $sql = "DELETE FROM " . $table . " WHERE id=" . $_POST['row_id'];

            $res = $db->query($sql);
            if ($res === true) {
                echo "<script>console.log('[OK]: Record deleted successfully')</script>";
            }
            else {
                echo "<script>console.error('[ERR]: ' + " . json_encode($db->error) . ")</script>";
            }

        }
    }

}
?>

  <html lang="en">
  <head>

    <!-- title and general meta -->
    <title>Kettering Student Clubs</title>
    <meta charset="utf-8">
    <meta name="description" content="Organizations and Clubs organized by Kettering University students.">
    <meta name="keywords" content="organizations,clubs,student,kettering,groups,university">

    <!-- css libraries and styles -->
    <link rel="stylesheet" href="/static/css/bootstrap.css">
    <link rel="stylesheet" href="/static/css/bootstrap-theme.css">
    <link rel="stylesheet" href="/static/css/fa.css">
    <link rel="stylesheet" href="/static/css/datatables.min.css">
    <link rel="stylesheet" href="/static/css/main.css">

    <!-- favicon icon -->
    <link rel="apple-touch-icon" sizes="180x180" href="/static/favicon/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon/favicon-16x16.png">
    <link rel="manifest" href="/static/favicon/site.webmanifest">
    <link rel="mask-icon" href="/static/favicon/safari-pinned-tab.svg" color="#5bbad5">
    <link rel="shortcut icon" href="/static/favicon/favicon.ico">
    <meta name="msapplication-TileColor" content="#da532c">
    <meta name="msapplication-config" content="/static/favicon/browserconfig.xml">
    <meta name="theme-color" content="#ffffff">

    <!-- CURRENT-PAGE css -->
    <link rel="stylesheet" href="/static/css/tables.css">

  </head>

  <body>

  <div class="container">

    <!-- header content -->
    <header>
      <nav class="nav-bar navbar-inverse wrapper-horizontal" role="navigation">
        <div>
          <a class="navbar-brand" href="/index.html">
            <img src="/static/images/bulldog.svg" alt="bulldog">
          </a>
        </div>

        <ul class="nav navbar-nav navbar-right">
          <li class="dropdown movable">
            <a href="#" class="dropdown-toggle" data-toggle="dropdown">
              <span class="caret"></span>
                <?php if (empty($_SESSION["id"])) {
                    echo "Guest";
                }
                else {
                    echo $_SESSION["name"];
                } ?>
            </a>
            <ul class="dropdown-menu" role="menu">
              <li class="divider"></li>
              <li>
                  <?php if (!empty($_SESSION["id"])): ?>
                    <a href="/mysql/views/logout.php"><span class="fa fa-power-off"></span>Logout</a>
                  <?php else: ?>
                    <a href="#"><span class="fa fa-power-on"></span>Login</a>
                  <?php endif; ?>
              </li>
            </ul>
          </li>
        </ul>
      </nav>

      <div class="top-bar hidden centered">
        <div class="message-bar"></div>
      </div>
    </header>

    <!-- CURRENT-PAGE content -->
    <section>

      <div class="wrapper-vertical">

        <!-- table title -->
        <div class="wrapper-horizontal edge-centered">
          <h4 style="Color:white"><?php echo ucwords($table) ?> Table Demo</h4>
        </div>

      </div>

      <br>
      <div class="clearfix"></div>

      <!-- table data -->
        <?php
        $template = new Template('templates/table.php');
        $template->set('db', $db);
        $template->set('table', $table);
        echo $template->render();
        ?>

    </section>

  </div>

  <!-- footer content -->
  <!-- not used yet -->
  <footer>
    <div class="bottom-bar hidden centered">
      <div></div>
    </div>
  </footer>

  <!-- interactive modals -->
  <?php
  $template = new Template('templates/modals.php');

  $sql = "SELECT * FROM " . $table;
  $res = $db->query($sql);
  $fields = $res->fetch_fields();
  /* show allow timestamp editing or relational ids */
  $form_body = new FormBody($fields, [12],
          ['id', 'approved', 'address_id', 'customer_id', 'agent_id', 'policy_id', 'premium_id', 'insurance_company_id']);


  $template->set('add_form_body', $form_body->render());
  $template->set('edit_form_body', $form_body->render());
  echo $template->render();
  ?>

  <!-- js libraries and default imports -->
  <script src="/static/js/jquery.js"></script>
  <script src="/static/js/bootstrap.js"></script>
  <script src="/static/js/datatables.min.js"></script>
  <script src="/static/js/main.js"></script>

  <!-- CURRENT-PAGE js -->
  <script src="/static/js/tables.js"></script>

  </body>
  </html>

<?php
// close db connection
$db->close();
?>