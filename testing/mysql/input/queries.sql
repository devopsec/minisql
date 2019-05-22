use global_insurance;

-- |========== get address records for a customer ==========|
select * from address t1, address_records t2
  where t2.customer_id = 1 and t1.id = t2.address_id;

-- |========== get agent managing each insurance policy for a customer ==========|
select (select t4.name where t4.id = t1.agent_id) as 'Home Insurance Agent',
    (select t4.name where t4.id = t2.agent_id) as 'Auto Insurance Agent',
    (select t4.name where t4.id = t3.agent_id) as 'Life Insurance Agent'
  from home_insurance_policy t1,
    auto_insurance_policy t2,
    life_insurance_policy t3,
    agent t4
  where t1.customer_id = 1
    or t2.customer_id = 1
    or t3.customer_id = 1;

-- | ========== get total coverage amount for an insurance company ==========|
select (SUM(t1.dwelling_coverage)+SUM(t1.liability_coverage)+SUM(t1.personal_property_coverage)+SUM(t1.living_expense_coverage)) as 'Home Insurance Coverage',
  (SUM(t2.coverage_amount)+SUM(t2.liability_coverage)+SUM(t2.uninsured_motorists_coverage)+SUM(t2.medical_coverage)+SUM(t2.personal_injury_coverage)) as 'Auto Insurance Coverage',
   SUM(t3.coverage) as 'Life Insurance Coverage'
  from home_insurance_policy t1,
    auto_insurance_policy t2,
    life_insurance_policy t3,
    insurance_company t4
  where t1.insurance_company_id = 1
    or t2.insurance_company_id = 1
    or t3.insurance_company_id = 1;

-- |========== show sales for arya stark ==========|
select * from sales where agent_id = 1;
-- "

-- |========== show premiums for a customer ==========|
select policy_type as 'Insurance Type',amount_due as 'Amount Due' from premium where customer_id = 1;

-- |========== update a policy and check premiums again ==========|
update auto_insurance_policy set coverage_amount = 34000, coverage_deductible = 200, uninsured_motorists_coverage = 50000, accident_forgiveness = 1 where customer_id = 1;
  select policy_type as 'Insurance Type',amount_due as 'Amount Due' from premium where customer_id = 1;

-- |========== update an insurance company and check premiums again ==========|
update insurance_company set home_rate = 0.0002559, auto_rate = 0.0028222, life_rate = 0.0003299 where id=1;
  select name,home_rate,auto_rate,life_rate from insurance_company;
  select policy_type,amount_due from premium;