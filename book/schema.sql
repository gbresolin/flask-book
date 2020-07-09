DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS category;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  isAdmin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  category_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  price DECIMAL (4,2) NOT NULL,
  state varchar (30) NOT NULL,
  image varchar (30) NULL,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (category_id) REFERENCES category (id)
);

CREATE TABLE category (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name varchar (50) NOT NULL,
  author_id INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

INSERT INTO user(id,username,password,isAdmin) VALUES('1', 'gregory', 'pbkdf2:sha256:150000$PU2JIbfY$c5f0273db55cd9e1911852298d2a985c7c6bac9ebcf0c368852061abb4a5a6e7',1);
INSERT INTO user(id,username,password,isAdmin) VALUES('2', 'george', 'pbkdf2:sha256:150000$PU2JIbfY$c5f0273db55cd9e1911852298d2a985c7c6bac9ebcf0c368852061abb4a5a6e7',1);
INSERT INTO user(id,username,password,isAdmin) VALUES('3', 'tony', 'pbkdf2:sha256:150000$VgMV7kx2$9b6414370ed48f11355f4e90781594ed8ce9406a040245142299d32f1bd57ed5',0);
INSERT INTO product(id,author_id,category_id,name,description,price,state,image) VALUES('1','1','1','Le pays des autres','Un livre bien écrit à découvrir','25','Neuf','book_220320201306.jpg');
INSERT INTO product(id,author_id,category_id,name,description,price,state,image) VALUES('2','1','3','Dragon Ball Super - Tome 11','Le combat contre le terrible criminel Moro fait toujours rage, et le Dai Kaio Shin endormi au fond de Boo s’est même joint à la danse. Le lieu de l’action quitte le vide sidéral pour se déplacer sur la nouvelle planète Namek.','6.9','Neuf','book_090720204834.jpg');
INSERT INTO category(id,name,author_id) VALUES('1', 'Histoire', '1');
INSERT INTO category(id,name,author_id) VALUES('2', 'Humour', '1');
INSERT INTO category(id,name,author_id) VALUES('3', 'Manga', '1');