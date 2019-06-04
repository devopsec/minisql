<?php

define('FORM_FIELD_NULL', '
    <input class="%2$s" name="field[%1$d]" type="hidden">');

define('FORM_FIELDS_MAPPING', array(
        "boolean" => '
    <div class="form-group">
      <label>%3$s: <input class="form-control %2$s" name="field[%1$d]" type="checkbox"></label>
    </div>',
        "number" => '
    <div class="form-group">
      <input class="form-control %2$s" type="number" name="field[%1$d]" placeholder="%3$s">
    </div>',
        "float" => '
    <div class="form-group">
      <input class="form-control %2$s" type="number" step="0.01" name="field[%1$d]" placeholder="%3$s">
    </div>',
        "date" => '
    <div class="form-group">
      <input class="form-control %2$s" type="date" name="field[%1$d]" placeholder="%3$s">
    </div>',
        "datetime" => '
    <div class="form-group">
      <input class="form-control %2$s" type="datetime-local" name="field[%1$d]" placeholder="%3$s">
    </div>',
        "time" => '
    <div class="form-group">
      <input class="form-control %2$s" type="time" name="field[%1$d]" placeholder="%3$s">
    </div>',
        "text" => '
    <div class="form-group">
      <input class="form-control %2$s" type="text" name="field[%1$d]" placeholder="%3$s">
    </div>'
));

define('MYSQL_TYPES_MAPPING', array(
        16 => FORM_FIELDS_MAPPING["boolean"], //BIT
        1 => FORM_FIELDS_MAPPING["boolean"], //BOOL|TINYINT
        2 => FORM_FIELDS_MAPPING["number"], //SMALLINT
        9 => FORM_FIELDS_MAPPING["number"], //MEDIUMINT
        3 => FORM_FIELDS_MAPPING["number"], //INTEGER
        8 => FORM_FIELDS_MAPPING["number"], //BIGINT
        4 => FORM_FIELDS_MAPPING["float"], //FLOAT
        5 => FORM_FIELDS_MAPPING["float"], //DOUBLE
        246 => FORM_FIELDS_MAPPING["float"], //DECIMAL
        10 => FORM_FIELDS_MAPPING["date"], //DATE
        12 => FORM_FIELDS_MAPPING["datetime"], //DATETIME
        7 => FORM_FIELDS_MAPPING["datetime"], //TIMESTAMP
        11 => FORM_FIELDS_MAPPING["time"], //TIME
        13 => FORM_FIELDS_MAPPING["date"], //YEAR
        254 => FORM_FIELDS_MAPPING["text"], //CHAR
        253 => FORM_FIELDS_MAPPING["text"], //VARCHAR
        252 => FORM_FIELDS_MAPPING["text"], //LONGTEXT
));

/**
 * Class FormBody
 * Dyanmically create a form body from mysql fields data
 */
class FormBody {
    protected $_fields_html;

    /**
     * FormBody constructor.
     * @param array $fields (mysql fields info)
     * @param array $hidden_types (mysql int value)
     */
    public function __construct($fields, $hidden_types = array(), $hidden_names = array()) {
        $auto_focus_set = false;
        for ($i = 0; $i < count($fields); $i++) {
            if (in_array($fields[$i]->type, $hidden_types) || in_array($fields[$i]->name, $hidden_names)) {
                $this->_fields_html[$i] = sprintf(FORM_FIELD_NULL, $i, $fields[$i]->name, ucwords(str_replace('_', ' ', $fields[$i]->name)));
                continue;
            }

            $html = sprintf(MYSQL_TYPES_MAPPING[$fields[$i]->type], $i, $fields[$i]->name, ucwords(str_replace('_', ' ', $fields[$i]->name)));
            if (!$auto_focus_set) {
                $re = '~(\<input.*?)(?=\>)~m';
                $html = preg_replace($re, '$1 autofocus', $html);
                $auto_focus_set = true;
            }
            $this->_fields_html[$i] = $html;
        }
    }

    public function render() {
        return join("\n", $this->_fields_html);
    }
}

?>