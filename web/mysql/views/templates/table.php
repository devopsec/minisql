<div class="table-responsive">
  <table id="dataTable" class="table table-striped table-centered table-hover">

    <thead>
    <tr class='element-row'>
        <?php
        $sql = 'SHOW COLUMNS FROM ' . $table;
        $res = $db->query($sql);
        $rows = $res->fetch_all();

        for ($i = 0; $i < count($rows) + 1; $i++) {
            if ($i === 0) {
                $field = $rows[$i][0];
                echo '<th data-field="' . $field . '">';
                /* add row button only for admin */
                if (!empty($_SESSION["id"]) && $_SESSION["id"] == 1) {
                    echo "<button id='open-Add' class='btn btn-success btn-md' title='Add Row' data-toggle='modal' data-target='#add'>Add </button>";
                }
                echo '</th>';

            }
            elseif ($i < count($rows)) {
                $field = $rows[$i][0];
                echo '<th data-field="' . $field . '">' . ucwords(str_replace('_', ' ', $field)) . '</th>';
            }
            else {
                if (!empty($_SESSION["id"]) && $_SESSION["id"] == 1) {
                    /* only show edit / delete column for admin */
                    echo "<th>Edit</th><th>Delete</th>";
                }
                else {
                    echo "<th></th><th></th>";
                }
            }
        }

        ?>
    </tr>
    </thead>
    <tbody>

    <?php
    $sql = "SELECT * FROM " . $table;
    $res = $db->query($sql);
    $rows = $res->fetch_all(MYSQLI_ASSOC);

    foreach ($rows as $row) {
        echo '<tr class="element-row">';

        $keys = array_keys($row);
        $vals = array_values($row);

        for ($i = 0; $i < count($row) + 1; $i++) {
            if ($i < count($row)) {
                echo '<td class="' . $keys[$i] . '">' . $vals[$i] . '</td>';
            }
            else {
                if (!empty($_SESSION["id"]) && $_SESSION["id"] == 1) {
                    echo "<td>
                    <button id='open-Update' class='open-Update btn btn-primary btn-xs' title='Edit Row'
                            data-toggle='modal' data-target='#edit'>
                      <span class='icon-edit'></span>
                    </button>
                  </td>
                  <td>
                    <button id='open-Delete' class='open-Delete btn btn-danger btn-xs' title='Delete Row'
                            data-toggle='modal' data-target='#delete'>
                      <span class='icon-delete'></span>
                    </button>
                  </td>";
                }
                else {
                    echo "<td></td><td></td>";
                }
            }
        }

        echo '</tr>';
    }

    $res->free();
    ?>
    </tbody>
  </table>
</div>