drop table if exists test_table;

create table test_table (
    field1 VARCHAR(255) PRIMARY KEY,
    field2 INTEGER 
);

-- some sample records
insert into test_table values ('abcde', 10), ('adkhe',12), ('badae', 3);