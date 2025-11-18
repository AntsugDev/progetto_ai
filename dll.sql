create table neo_patentato(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table sesso(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table zona(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table tipologia_auto(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table nuovo_usato(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table formula_acquisto(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table neo_patentato(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table sesso(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table zona(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table tipologia_auto(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table nuovo_usato(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table formula_acquisto(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);
create table model(
id int(11) not null auto_increment,
cliente varchar(255) not null,
eta int(11) null,
neo_patentato_id int(11) not null,
nr_figli int(11) null default 0,
reddito_mensie float not null,
altre_spese float not null,
diff_reddito float not null,
sesso_id int(11) not null,
zona_id int(11) not null,
tipologia_auto_id int(11) not null,
nuovo_usato_id int(11) not null,
costo_auto float not null,
eta_veicolo int(11) null default 0,
oneri_accessori float not null,
anticipo float not null,
tan float not null,
formula_acquisto_id int(11) not null,
nr_rate int(11) not null,
importo_finanziato float  null,
rata float null,
sostenibilita float null,
coefficiente_k float null,
re float null,
rs float null,
rd float null,
rt float null,
decisione_AI varchar(1000) null,
is_simulation char(1) null default 'N',
constraint fk_neo_patentato foreign key(neo_patentato_id) references neo_patentato(id),
constraint fk_sesso foreign key(sesso_id) references sesso(id),
constraint fk_zona foreign key(zona_id) references zona(id),
constraint fk_tipologia_auto foreign key(tipologia_auto_id) references tipologia_auto(id),
constraint fk_nuovo_usato foreign key(nuovo_usato_id) references nuovo_usato(id),
constraint fk_formula_acquisto foreign key(formula_acquisto_id) references formula_acquisto(id),
primary key(id)
);
create table simulation_type(
id int(11) not null auto_increment,
testo varchar(255) not null,
primary key(id)
);

create table simulation(
id int(11) auto_increment,
model_id int(11) not null,
simulation_type_id int(11) not null,
anticipo float null,
importo_finanziamento float null,
importo_rata float null,
nr_rata int null,
rata float null,
sostenibilita float null,
decisione varchar(1000) null,
decision_ai  varchar(1000) null,
constraint fk_model foreign key(model_id) references model(id),
constraint fk_simulation_type foreign key(simulation_type_id) references simulation_type(id),
primary key(id)
);

---------------------------------------------------------------------------------------------------------------------


insert into formula_acquisto (testo) values ('totale con bonifico');
insert into formula_acquisto (testo) values ('finanziamento classico auto usata');
insert into formula_acquisto (testo) values ('finanziamento a 3 anni auto nuova');

#----------------------------------

insert into neo_patentato  (testo) values ('Si');
insert into neo_patentato  (testo) values ('No');

#--------------------------------------

insert into nuovo_usato   (testo) values ('Nuova');
insert into nuovo_usato  (testo) values ('Usata');

#--------------------------------------------------

insert into sesso   (testo) values ('uomo');
insert into sesso  (testo) values ('donna');
insert into sesso  (testo) values ('altro');

#-------------------------------------------------

insert into simulation_type   (testo) values ('Simulazione di anticipo per auto usata');
insert into simulation_type   (testo) values ('Simulazione di aumento numero di rate');

#-------------------------------------------------------------

insert into tipologia_auto    (testo) values ('utilitaria');
insert into tipologia_auto    (testo) values ('suv');
insert into tipologia_auto    (testo) values ('berlina');
insert into tipologia_auto    (testo) values ('monovolume');
insert into tipologia_auto    (testo) values ('station wagon');

#-----------------------------------------------------------------

insert into zona    (testo) values ('nord ovest');
insert into zona    (testo) values ('nord est');
insert into zona    (testo) values ('centro');
insert into zona    (testo) values ('sud');
insert into zona    (testo) values ('isole');





