-- hh_mysql_query.sql

USE job_base__hh_pages.db;

-- Дата публикации не задана

SELECT * FROM vacancies WHERE date_publication = "2023-02-06";

SELECT * FROM vacancies_list_itemloader WHERE _id = "76273162";

SELECT DISTINCT date_publication FROM vacancies;  

-- Валюта не задана

SELECT * FROM vacancies WHERE salary_cur = '';

SELECT * FROM vacancies ORDER BY date_publication ASC; 
-- DESC;

