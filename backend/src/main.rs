use std::collections::HashMap;

use actix_web::{App, HttpServer, web::Json};
use actix_web_static_files::ResourceFiles;
use static_files::Resource;
use serde::{Deserialize, Serialize};

use dotenv::dotenv;
use diesel::sqlite::SqliteConnection;
use r2d2_diesel::ConnectionManager;
use r2d2::Pool;
use std::env;
use diesel::prelude::*;
use diesel::{Queryable, Insertable};
use uuid::Uuid;

#[macro_use] 
extern crate diesel;
extern crate dotenv;

use actix_web::{get, web, Responder, HttpResponse};

fn generate() -> HashMap<&'static str, Resource> {
    include!(concat!(env!("OUT_DIR"), "/generated.rs"))
}

diesel::table! {
    books (id) {
        id -> Text,
        name -> Text,
        description -> Text,
        file -> Text,
        preview -> Text,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

#[derive(Deserialize, Serialize, Queryable, Insertable)]
#[table_name = "books"]
pub struct Book {
    pub id: String,
    pub name: String,
    pub description: String,
    pub file: String,
    pub preview: String,    
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
}

pub type DbPool = Pool<ConnectionManager<SqliteConnection>>;

impl Book {
    pub fn list(conn: &SqliteConnection) -> Vec<Self> {
        books::dsl::books.load::<Book>(conn).expect("Error loading users")
    }

    pub fn by_id(id: &str, conn: &SqliteConnection) -> Option<Self> {
        books::dsl::books.find(id).get_result::<Book>(conn).ok()
    }

    pub fn by_name(name_str: &str, conn: &SqliteConnection) -> Option<Self> {
        use books::dsl::name;

        books::dsl::books.filter(name.eq(name_str)).first::<Book>(conn).ok()
    }
}

pub fn establish_connection() -> DbPool {
    dotenv().ok();

    let database_url = env::var("DATABASE_URL").unwrap_or(String::from("./database.db"));
    let manager = ConnectionManager::<SqliteConnection>::new(&database_url);
    
    r2d2::Pool::builder().build(manager).expect("Failed to create DB pool.")
}

#[get("/books")]
pub async fn api_books(pool: web::Data<DbPool>) -> impl Responder {
    // let a_books:Vec<Book> = Vec::new();

    let conn = pool.get().unwrap();
    let a_books = Book::list(&conn);

    HttpResponse::Ok().json(a_books)
}

#[get("/book")]
pub async fn api_book(id: web::Path<String>, pool: web::Data<DbPool>) -> impl Responder {
    let conn = pool.get().unwrap();
    let s_id = id.to_string();

    let o_book = Book::by_id(&id, &conn);

    HttpResponse::Ok().json(o_book)
}


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("=== start ===");
    let s_host = env::var("HOST").unwrap_or(String::from("0.0.0.0"));
    let s_port = env::var("PORT").unwrap_or(String::from("8181"));
    let s_bind = format!("{}:{}", s_host, s_port);

    println!("listening: {}", s_bind);
    
    let conn_pool = establish_connection();

    HttpServer::new(move || {
        let generated = generate();
        App::new()
            .data(conn_pool.clone())
            .service(
                web::scope("/api")
                    .service(api_books)
                    .service(api_book)
            )
            .service(ResourceFiles::new("/", generated))
    })
    .bind(s_bind)?
    .run()
    .await
}
