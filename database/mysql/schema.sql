DROP DATABASE IF EXISTS global_insurance;
CREATE DATABASE global_insurance;

USE global_insurance;

DROP TABLE IF EXISTS address;
CREATE TABLE address (
  id INT(11) NOT NULL AUTO_INCREMENT,
  apartment VARCHAR(255) DEFAULT '',
  street VARCHAR(255) NOT NULL,
  city VARCHAR(255) NOT NULL,
  state VARCHAR(255) NOT NULL,
  country VARCHAR(255) NOT NULL,
  zipcode VARCHAR(255) NOT NULL,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

DROP TABLE IF EXISTS agent;
CREATE TABLE agent (
  id INT(11) NOT NULL AUTO_INCREMENT,
  address_id INT(11) NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(255) NOT NULL,
  salary INT(10) DEFAULT 0,
  commision float(5,4) DEFAULT 0.00,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (address_id) REFERENCES address (id)
);

DROP TABLE IF EXISTS customer;
CREATE TABLE customer (
  id INT(11) NOT NULL AUTO_INCREMENT,
  address_id INT(11) NOT NULL,



  name VARCHAR(255) NOT NULL,




  phone VARCHAR(255) NOT NULL,
  dob DATE NOT NULL,
  sex VARCHAR(255) NOT NULL, -- male | female | other
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (address_id) REFERENCES address (id)
);

DROP TABLE IF EXISTS customer_address_records;
CREATE TABLE address_records (
  customer_id INT(11) NOT NULL,
  address_id INT(11) NOT NULL,
  PRIMARY KEY (customer_id, address_id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (address_id) REFERENCES address (id)
);

# -- create address_record when customer address created
# DROP TRIGGER IF EXISTS insert_address_record;
# DELIMITER //
# CREATE TRIGGER insert_address_record AFTER INSERT ON customer
#   FOR EACH ROW
#   BEGIN
#     INSERT IGNORE INTO address_records VALUES (NEW.id, NEW.address_id);
#   END;//
# DELIMITER ;
#
# -- create address_record when customer address updated
# DROP TRIGGER IF EXISTS update_address_record;
# DELIMITER //
# CREATE TRIGGER update_address_record AFTER UPDATE ON customer
#   FOR EACH ROW
#   BEGIN
#     INSERT IGNORE INTO address_records VALUES (NEW.id, NEW.address_id);
#   END;//
# DELIMITER ;

DROP TABLE IF EXISTS premium;
CREATE TABLE premium (
  id INT(11) NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NOT NULL,
  agent_id INT(11) NOT NULL,
  policy_id INT(11) NOT NULL, -- constrained by application
  policy_type VARCHAR(255) NOT NULL, -- home | auto | life
  policy_coverage INT(11) NOT NULL,
  amount_due INT(11) NOT NULL, -- total coverage * (rate - (deductible / total coverage * 0.01))
  date_due DATE NOT NULL,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (agent_id) REFERENCES agent (id)
);

DROP TABLE IF EXISTS insurance_company;
CREATE TABLE insurance_company (
  id INT(11) NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  address_id INT(11) NOT NULL,
  home_rate float(9,8) DEFAULT 0.000025,
  auto_rate float(9,8) DEFAULT 0.00028,
  life_rate float(9,8) DEFAULT 0.000021,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (address_id) REFERENCES address (id)
);

-- update premiums when insurance_company rates change
DROP TRIGGER IF EXISTS update_insurance_company_premium;
DELIMITER //
CREATE TRIGGER update_insurance_company_premium AFTER UPDATE ON insurance_company
  FOR EACH ROW
  BEGIN
    UPDATE premium p
    LEFT JOIN (
        select id as policy_id,'home' as policy_type,NEW.home_rate as rate,coverage_deductible as deductible from home_insurance_policy t1 where t1.insurance_company_id=NEW.id
        union select id as policy_id,'auto' as policy_type,NEW.auto_rate as rate,coverage_deductible as deductible from auto_insurance_policy t2 where t2.insurance_company_id=NEW.id
        union select id as policy_id,'life' as policy_type,NEW.life_rate as rate,coverage_deductible as deductible from life_insurance_policy t3 where t3.insurance_company_id=NEW.id
      ) as temp USING (policy_id,policy_type)
    SET amount_due = (p.policy_coverage*((temp.rate)-((temp.deductible)/p.policy_coverage*0.01)));
  END;//
DELIMITER ;

DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
  id INT(11) NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NOT NULL,
  agent_id INT(11) NOT NULL,
  premium_id INT(11) DEFAULT NULL,
  type VARCHAR(255) NOT NULL, -- appt | auto | home | life
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (agent_id) REFERENCES agent (id),
  CONSTRAINT FOREIGN KEY (premium_id) REFERENCES premium (id)
);

DROP TABLE IF EXISTS home_insurance_policy;
CREATE TABLE home_insurance_policy (
  id INT(11) NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NOT NULL,
  agent_id INT(11) NOT NULL,
  insurance_company_id INT(11) NOT NULL,
  employer_name VARCHAR(255) NOT NULL,
  dwelling_coverage INT(11) NOT NULL DEFAULT 0,
  liability_coverage INT(11) NOT NULL DEFAULT 200000,
  personal_property_coverage INT(11) NOT NULL DEFAULT 0,
  living_expense_coverage INT(11) NOT NULL DEFAULT 0,
  coverage_deductible INT(11) NOT NULL DEFAULT 500,
  approved TINYINT(1) NOT NULL DEFAULT 0,
  active TINYINT(1) NOT NULL DEFAULT 0,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (agent_id) REFERENCES agent (id),
  CONSTRAINT FOREIGN KEY (insurance_company_id) REFERENCES insurance_company (id)
);

-- update premium when home insurance is sold
DROP TRIGGER IF EXISTS insert_home_insurance_premium;
DELIMITER //
CREATE TRIGGER insert_home_insurance_premium AFTER INSERT ON home_insurance_policy
  FOR EACH ROW
  BEGIN
    DECLARE total_coverage INT;
    SET total_coverage := (NEW.dwelling_coverage+NEW.liability_coverage+NEW.personal_property_coverage+NEW.living_expense_coverage);
    INSERT INTO premium VALUES (
      DEFAULT,NEW.customer_id,NEW.agent_id,NEW.id,'home',total_coverage,
      (total_coverage*((SELECT home_rate FROM insurance_company WHERE id = NEW.insurance_company_id)-(NEW.coverage_deductible/total_coverage*0.01))),
      (CURRENT_DATE+INTERVAL 1 YEAR),DEFAULT,DEFAULT
    );
  END;//
DELIMITER ;

-- update premium when home insurance is updated
DROP TRIGGER IF EXISTS update_home_insurance_premium;
DELIMITER //
CREATE TRIGGER update_home_insurance_premium AFTER UPDATE ON home_insurance_policy
  FOR EACH ROW
  BEGIN
    DECLARE total_coverage INT;
    SET total_coverage := (NEW.dwelling_coverage+NEW.liability_coverage+NEW.personal_property_coverage+NEW.living_expense_coverage);
    UPDATE premium SET policy_coverage = total_coverage,
      amount_due = (total_coverage*((SELECT home_rate FROM insurance_company WHERE id = NEW.insurance_company_id)-(NEW.coverage_deductible/total_coverage*0.01)))
    WHERE policy_id = NEW.id and policy_type = 'home';
  END;//
DELIMITER ;

-- create sales record when home insurance is sold
DROP TRIGGER IF EXISTS insert_home_insurance_sales;
DELIMITER //
CREATE TRIGGER insert_home_insurance_sales AFTER INSERT ON home_insurance_policy
  FOR EACH ROW FOLLOWS insert_home_insurance_premium
  BEGIN
    DECLARE premium_id INT;
    SELECT id INTO premium_id FROM premium WHERE policy_id = NEW.id and policy_type = 'home';
    INSERT INTO sales VALUES (DEFAULT,NEW.customer_id,NEW.agent_id,premium_id,'home',DEFAULT,DEFAULT);
  END;//
DELIMITER ;

DROP TABLE IF EXISTS auto_insurance_policy;
CREATE TABLE auto_insurance_policy (
  id INT(11) NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NOT NULL,
  agent_id INT(11) NOT NULL,
  insurance_company_id INT(11) NOT NULL,
  coverage_type VARCHAR(255) NOT NULL DEFAULT 'standard', -- standard | collision | comprehensive
  coverage_amount INT(11) NOT NULL DEFAULT 0,
  coverage_deductible INT(11) NOT NULL DEFAULT 500,
  license_number VARCHAR(255) NOT NULL,
  license_state VARCHAR(255) NOT NULL,
  num_pts SMALLINT(5) NOT NULL,
  liability_coverage INT(11) NOT NULL DEFAULT 200000,
  uninsured_motorists_coverage INT(11) NOT NULL DEFAULT 0,
  medical_coverage INT(11) NOT NULL DEFAULT 50000,
  personal_injury_coverage INT(11) NOT NULL DEFAULT 1000000000,
  valid_thru DATE NOT NULL,
  accident_forgiveness TINYINT(1) NOT NULL DEFAULT 0,
  approved TINYINT(1) NOT NULL DEFAULT 0,
  active TINYINT(1) NOT NULL DEFAULT 0,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (agent_id) REFERENCES agent (id),
  CONSTRAINT FOREIGN KEY (insurance_company_id) REFERENCES insurance_company (id)
);

-- update premium when auto insurance is sold
DROP TRIGGER IF EXISTS insert_auto_insurance_premium;
DELIMITER //
CREATE TRIGGER insert_auto_insurance_premium AFTER INSERT ON auto_insurance_policy
  FOR EACH ROW
  BEGIN
    DECLARE total_coverage INT;
    SET total_coverage := (NEW.coverage_amount+NEW.liability_coverage+NEW.uninsured_motorists_coverage+NEW.medical_coverage+NEW.personal_injury_coverage);
    INSERT INTO premium VALUES (
      DEFAULT,NEW.customer_id,NEW.agent_id,NEW.id,'auto',total_coverage,
      (total_coverage*((SELECT auto_rate FROM insurance_company WHERE id = NEW.insurance_company_id)-(NEW.coverage_deductible/total_coverage*0.01))),
      (CURRENT_DATE+INTERVAL 1 YEAR),DEFAULT,DEFAULT
    );
  END;//
DELIMITER ;

-- update premium when auto insurance is updated
DROP TRIGGER IF EXISTS update_auto_insurance_premium;
DELIMITER //
CREATE TRIGGER update_auto_insurance_premium AFTER UPDATE ON auto_insurance_policy
  FOR EACH ROW
  BEGIN
    DECLARE total_coverage INT;
    SET total_coverage := (NEW.coverage_amount+NEW.liability_coverage+NEW.uninsured_motorists_coverage+NEW.medical_coverage+NEW.personal_injury_coverage);
    UPDATE premium SET policy_coverage = total_coverage,
      amount_due = (total_coverage*((SELECT auto_rate FROM insurance_company WHERE id = NEW.insurance_company_id)-(NEW.coverage_deductible/total_coverage*0.01)))
    WHERE policy_id = NEW.id and policy_type = 'auto';
  END;//
DELIMITER ;

-- create sales record when auto insurance is sold
DROP TRIGGER IF EXISTS insert_auto_insurance_sales;
DELIMITER //
CREATE TRIGGER insert_auto_insurance_sales AFTER INSERT ON auto_insurance_policy
  FOR EACH ROW FOLLOWS insert_auto_insurance_premium
  BEGIN
    DECLARE premium_id INT;
    SELECT id INTO premium_id FROM premium WHERE policy_id = NEW.id and policy_type = 'auto';
    INSERT INTO sales VALUES (DEFAULT,NEW.customer_id,NEW.agent_id,premium_id,'auto',DEFAULT,DEFAULT);
  END;//
DELIMITER ;

DROP TABLE IF EXISTS life_insurance_policy;
CREATE TABLE life_insurance_policy (
  id INT(11) NOT NULL AUTO_INCREMENT,
  agent_id INT(11) NOT NULL,
  customer_id INT(11) NOT NULL,
  insurance_company_id INT(11) NOT NULL,
  employer_name VARCHAR(255) NOT NULL,
  coverage INT(11) NOT NULL DEFAULT 500000,
  coverage_deductible INT(11) NOT NULL DEFAULT 500,
  approved TINYINT(1) NOT NULL DEFAULT 0,
  active TINYINT(1) NOT NULL DEFAULT 0,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (agent_id) REFERENCES agent (id),
  CONSTRAINT FOREIGN KEY (insurance_company_id) REFERENCES insurance_company (id)
);

-- update premium when life insurance is sold
DROP TRIGGER IF EXISTS insert_life_insurance_premium;
DELIMITER //
CREATE TRIGGER insert_life_insurance_premium AFTER INSERT ON life_insurance_policy
  FOR EACH ROW
  BEGIN
    INSERT INTO premium VALUES (
      DEFAULT,NEW.customer_id,NEW.agent_id,NEW.id,'life',NEW.coverage,
      (NEW.coverage*((SELECT life_rate FROM insurance_company WHERE id = NEW.insurance_company_id)-(NEW.coverage_deductible/NEW.coverage*0.01))),
      (CURRENT_DATE+INTERVAL 1 YEAR),DEFAULT,DEFAULT
    );
  END;//
DELIMITER ;

-- update premium when life insurance is updated
DROP TRIGGER IF EXISTS update_life_insurance_premium;
DELIMITER //
CREATE TRIGGER update_life_insurance_premium AFTER UPDATE ON life_insurance_policy
  FOR EACH ROW
  BEGIN
    UPDATE premium SET policy_coverage = NEW.coverage,
      amount_due = (NEW.coverage*((SELECT life_rate FROM insurance_company WHERE id = NEW.insurance_company_id)-(NEW.coverage_deductible/NEW.coverage*0.01)))
    WHERE policy_id = NEW.id and policy_type = 'life';
  END;//
DELIMITER ;

-- create sales record when life insurance is sold
DROP TRIGGER IF EXISTS insert_life_insurance_sales;
DELIMITER //
CREATE TRIGGER insert_life_insurance_sales AFTER INSERT ON life_insurance_policy
  FOR EACH ROW FOLLOWS insert_life_insurance_premium
  BEGIN
    DECLARE premium_id INT;
    SELECT id INTO premium_id FROM premium WHERE policy_id = NEW.id and policy_type = 'life';
    INSERT INTO sales VALUES (DEFAULT,NEW.customer_id,NEW.agent_id,premium_id,'life',DEFAULT,DEFAULT);
  END;//
DELIMITER ;

DROP TABLE IF EXISTS beneficiaries;
CREATE TABLE beneficiaries (
  id INT(11) NOT NULL AUTO_INCREMENT,
  policy_id INT(11) NOT NULL,
  address_id INT(11) NOT NULL,
  name VARCHAR(255) NOT NULL,
  percentage float(5,2) DEFAULT 0.00, -- constrained by application
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (policy_id) REFERENCES life_insurance_policy (id),
  CONSTRAINT FOREIGN KEY (address_id) REFERENCES address (id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS vehicle;
CREATE TABLE vehicle (
  id INT(11) NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NOT NULL,
  policy_id INT(11) DEFAULT NULL,
  year DATE NOT NULL,
  make VARCHAR(255) NOT NULL,
  model VARCHAR(255) NOT NULL,
  style VARCHAR(255) NOT NULL,
  mileage MEDIUMINT(255) NOT NULL,
  license_plate VARCHAR(255) NOT NULL,
  vin VARCHAR(255) DEFAULT '',
  work_vehicle TINYINT(1) NOT NULL,
  security_equipped TINYINT(1) NOT NULL DEFAULT 0,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  modification_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT FOREIGN KEY (customer_id) REFERENCES customer (id),
  CONSTRAINT FOREIGN KEY (policy_id) REFERENCES auto_insurance_policy (id)
);
