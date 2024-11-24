import sqlite3
import pandas as pd

# Create a connection to the SQLite database
conn = sqlite3.connect('blog.db')
c = conn.cursor()

# Create a table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS posts (
    author TEXT NOT NULL, 
    title TEXT NOT NULL, 
    content TEXT NOT NULL, 
    date DATE NOT NULL
)
''')

# Close the cursor first
c.close()

# Then close the connection
conn.close()

def add_post(author, title, content, date):
    try:
        # Connect to the database and create a cursor using a context manager
        with sqlite3.connect('blog.db') as conn:
            c = conn.cursor()
            # Insert a new row into the posts table
            c.execute('INSERT INTO posts (author, title, content, date) VALUES (?, ?, ?, ?)',
                      (author, title, content, date))
            # Commit the changes (not strictly necessary as the 'with' statement does it)
            conn.commit()
    except sqlite3.Error as e:
        # Print the error message
        print(f"Database error: {e}")
    except Exception as e:
        # Print any other error
        print(f"Error: {e}")

def get_all_posts():
    try:
        # Connect to the database using a context manager
        with sqlite3.connect('blog.db') as conn:
            # Create a cursor and execute the query
            c = conn.cursor()
            c.execute('SELECT * FROM posts')
            # Fetch all the results
            data = c.fetchall()
            # Return the data
            return data
    except sqlite3.Error as e:
        # Print the error message
        print(f"Database error: {e}")
        return None  # Return None if there is an error
    except Exception as e:
        # Handle any other exceptions
        print(f"Unexpected error: {e}")
        return None

def get_post_by_title(title):
    try:
        # Connect to the database
        conn = sqlite3.connect('blog.db')
        # Create a cursor object
        c = conn.cursor()
        # Select the row from the posts table that matches the title
        c.execute('SELECT * FROM posts WHERE title=?', (title,))
        # Fetch the result
        data = c.fetchone()
        # Close the connection and the cursor
        conn.close()
        c.close()
        # Return the data
        return data
    except sqlite3.Error as e:
        # Print the error message
        print(e)

def delete_post(title):
    try:
        # Connect to the database
        conn = sqlite3.connect('blog.db')
        # Create a cursor object
        c = conn.cursor()
        # Delete the row from the posts table that matches the title
        c.execute('DELETE FROM posts WHERE title=?', (title,))
        # Save the changes to the database
        conn.commit()
        # Close the connection and the cursor
        conn.close()
        c.close()
    except sqlite3.Error as e:
        # Print the error message
        print(e)

import streamlit as st
import sqlite3
import pandas as pd

# Plantillas para mostrar posts
title_temp = """
<div style="background-color:#f9f9f9;padding:10px;margin:10px 0;border-radius:5px;">
    <h4>{}</h4>
    <h6>By: {}</h6>
    <p>{}</p>
</div>
"""
post_temp = """
<div style="background-color:#f9f9f9;padding:10px;margin:10px 0;border-radius:5px;">
    <h4>{}</h4>
    <h6>By: {}</h6>
    <small>{}</small>
    <p>{}</p>
</div>
"""

# Función para conectar con la base de datos
def connect_db():
    return sqlite3.connect('blog.db')

# Función para obtener todos los posts
def get_all_posts():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT author, title, content, date FROM posts")
    posts = c.fetchall()
    conn.close()
    return posts

# Función para agregar un post
def add_post(author, title, content, date):
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO posts (author, title, content, date) VALUES (?, ?, ?, ?)", 
              (author, title, content, date))
    conn.commit()
    conn.close()

# Función para eliminar un post
def delete_post(title):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE title = ?", (title,))
    conn.commit()
    conn.close()

# Sidebar Menu
menu = ["Home", "View Posts", "Add Post", "Search", "Manage"]
choice = st.sidebar.selectbox("Menu", menu)

# Home
if choice == "Home":
    st.title("Welcome to my blog")
    st.write("This is a simple blog app built with Streamlit and Python.")
    st.write("You can view, add, search, and manage posts using the sidebar menu.")
    st.write("Enjoy!")

# View Posts
elif choice == "View Posts":
    st.title("View Posts")
    st.write("Here you can see all the posts in the blog.")
    posts = get_all_posts()
    for post in posts:
        st.markdown(title_temp.format(post[1], post[0], post[2][:50] + "..."), unsafe_allow_html=True)
        if st.button("Read More", key=post[1]):
            st.markdown(post_temp.format(post[1], post[0], post[3], post[2]), unsafe_allow_html=True)

# Add Post
elif choice == "Add Post":
    st.title("Add Post")
    with st.form(key="add_form"):
        author = st.text_input("Author")
        title = st.text_input("Title")
        content = st.text_area("Content")
        date = st.date_input("Date")
        submit = st.form_submit_button("Submit")
    if submit:
        add_post(author, title, content, date)
        st.success("Post added successfully")

# Search
elif choice == "Search":
    st.title("Search")
    query = st.text_input("Enter your query")
    if query:
        posts = get_all_posts()
        results = [post for post in posts if query.lower() in post[0].lower() or query.lower() in post[1].lower()]
        if results:
            st.write(f"Found {len(results)} matching posts:")
            for result in results:
                st.markdown(title_temp.format(result[1], result[0], result[2][:50] + "..."), unsafe_allow_html=True)
                if st.button("Read More", key=result[1]):
                    st.markdown(post_temp.format(result[1], result[0], result[3], result[2]), unsafe_allow_html=True)
        else:
            st.write("No matching posts found")

# Manage
elif choice == "Manage":
    st.title("Manage")
    titles = [post[1] for post in get_all_posts()]
    title = st.selectbox("Select a post to delete", titles)
    if st.button("Delete"):
        delete_post(title)
        st.success("Post deleted successfully")
    if st.checkbox("Show statistics"):
        posts = get_all_posts()
        df = pd.DataFrame(posts, columns=["author", "title", "content", "date"])
        st.write("Number of posts:", len(posts))
        st.write("Number of authors:", len(df["author"].unique()))
        st.write("Most recent post:", df["date"].max())
        st.write("Oldest post:", df["date"].min())
        st.bar_chart(df["author"].value_counts())



