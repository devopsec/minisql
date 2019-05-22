CREATE USER IF NOT EXISTS 'gia_admin'@'%' IDENTIFIED BY 'global_admin_enter';
GRANT USAGE ON *.* TO 'gia_admin'@'%'  IDENTIFIED BY 'global_admin_enter';
GRANT ALL PRIVILEGES ON `global_insurance`.* TO 'gia_admin'@'%'  IDENTIFIED BY 'global_admin_enter';
