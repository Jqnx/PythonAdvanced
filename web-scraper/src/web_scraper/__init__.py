import requests

def main() -> None:
    id: int = int(input("Welke post wil je zien? "))

    post = get_post(id)
    print(f"{post["title"]} ({post["views"]} views)")

    comments = get_comments(id)
    for comment in comments:
        print(f"- {comment["text"]}")

def get_post(post_id: int):
    r = requests.get("http://localhost:3000/posts")
    json = r.json()
    for post in json:
        if int(post["id"]) == post_id:
            return post

def get_comments(post_id: int):
    r = requests.get("http://localhost:3000/comments")
    json = r.json()
    comments: list = []
    for comment in json:
        if int(comment["postId"]) == post_id:
            comments.append(comment)
    return comments

if __name__ == "__main__":
    main()
