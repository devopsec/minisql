use global_insurance;

-- create example data
insert into address values (DEFAULT,DEFAULT,'1234 fake st.','detroit','mi','united states','00000',DEFAULT,DEFAULT);
insert into address values (DEFAULT,DEFAULT,'1234 fake rd.','flint','mi','united states','00000',DEFAULT,DEFAULT);
insert into address values (DEFAULT,DEFAULT,'1234 fake blvd.','grand rapids','mi','united states','00000',DEFAULT,DEFAULT);
insert into address values (DEFAULT,DEFAULT,'1234 fake circle.','lansing','mi','united states','00000',DEFAULT,DEFAULT);
insert into address values (DEFAULT,DEFAULT,'1234 faker st.','detroit','mi','united states','00000',DEFAULT,DEFAULT);
insert into address values (DEFAULT,DEFAULT,'1234 fakest st.','detroit','mi','united states','00000',DEFAULT,DEFAULT);

insert into agent values (DEFAULT,3,'arya stark','astark@gmail.com','012-345-6789',100000,0.02,DEFAULT,DEFAULT);

insert into customer values (DEFAULT,1,'julian assange','rjames@gmail.com','012-345-6789',DATE('1993-01-01'),'male',DEFAULT,DEFAULT);
insert into customer values (DEFAULT,2,'edward snowden','esnowden@gmail.com','012-345-6789',DATE('1993-01-01'),'male',DEFAULT,DEFAULT);
update customer set address_id = 5 where id = 1;
update customer set address_id = 6 where id = 1;

insert into insurance_company values (DEFAULT,'pwning inc',4,DEFAULT,DEFAULT,DEFAULT);

insert into home_insurance_policy values (DEFAULT,1,1,1,'The Rock Johnson',250000,DEFAULT ,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT);
insert into auto_insurance_policy values (DEFAULT,1,1,1,DEFAULT,28000,DEFAULT,'0987654321','mi',12,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DATE('2020-01-01'),DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT);
insert into life_insurance_policy values (DEFAULT,1,1,1,'The Rock Johnson',400000,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT);
