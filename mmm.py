from models import m_client, Article, User, Category
from workers.manager import exc_handler

@exc_handler
def query_all_article(**kwargs):
    """Query Article Info."""
    sess = kwargs.get('sess')

    article_list = sess.query(
        Article.article_id,
        Article.content
    ).all()

    head_list = ['article_id', 'content']

    article_list = [dict(zip(head_list, article)) for article in article_list]

    return article_list


def main():
    mongo_article = m_client.article_content
    article_list = query_all_article()

    for article in article_list:
        mongo_article.update_one(dict(article_id=article['article_id']), {'$set': {'content': article['content']}}, upsert=True)


if __name__ == '__main__':
    main()
