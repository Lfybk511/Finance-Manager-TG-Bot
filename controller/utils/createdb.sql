create table category(
    codename varchar(255) primary key,
    name varchar(255),
    aliases text
);

create table expense(
    user_id integer,
    id integer primary key ,
    amount integer,
    created datetime,
    category_codename integer,
    raw_text text,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

insert into category (codename, name, aliases)
values
    ("Sweets", "Сладости", "сладости, печеньки"),
    ("coffee", "Кофе", "капучино, латте"),
    ("Diningroom", "Столовая", "столовая, столовка"),
    ("fastfood", "Фастфуд", "ресторан, рест, мак, макдональдс, макдак, kfc, кфс"),
    ("taxi", "такси", "яндекс такси, yandex taxi, такси, таксо"),
    ("other", "прочее", ""),
    ("saved", "сохранил", "сохранил, сэкономил, не потратил, не купил");

