create table category(
    codename varchar(255) primary key,
    name varchar(255),
    aliases text
);

insert into category (codename, name, aliases)
values
    ("saved", "💵 сохранил", "сохранил,сохранила, сэкономил,сэкономила, не потратил, не потратила, не купил, не купила"),
    ("other", "✨ прочее", ""),
    ("Sweets", "🍫 Сладости", "сладости, печеньки"),
    ("coffee", "☕ Кофе", "капучино, латте, кофе"),
    ("Diningroom", "🍜 Столовая", "столовая, столовка"),
    ("fastfood", "🍔 Фастфуд", "ресторан, рест, мак, макдональдс, макдак, kfc, кфс"),
    ("taxi", "🚕 такси", "яндекс такси, yandex taxi, такси, таксо"),
    ("alcohol", "🍷 алкоголь", "алкоголь, пиво, сидр, вино"),
    ("nicotine", "🚬 никотин", "сигареты, сиги, hqd");
