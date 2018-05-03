# coding:utf-8

from handlers.lazor import article, category, file, guard, log, user

LAZOR_ROUTES = [
    (r'/middle/article', article.Article),
    (r'/middle/generate-id', article.ArticleId),
    (r'/middle/article/user-list', article.UserArticleList),
    (r'/middle/article/index-list', article.IndexArticleList),
    (r'/middle/article/publish-state', article.ArticlePublishState),
    (r'/middle/article/order', article.ArticleOrder),
    (r'/middle/category', category.Category),
    (r'/middle/category/index', category.CategoryIndexList),
    (r'/middle/category/order', category.CategoryOrder),
    (r'/middle/file', file.File),
    (r'/middle/image', file.Image),
    (r'/middle/image/record/.*', file.ImageRecord),
    (r'/middle/guard/auth', guard.AuthGuard),
    (r'/middle/guard/owner', guard.ArticleOwnerGuard),
    (r'/middle/log/access', log.AccessLog),
    (r'/middle/log/credit', log.Credit),
    (r'/middle/js/loading.js', log.Favicon),
    (r'/middle/user', user.User),
    (r'/middle/user/profile', user.UserProfile),
    (r'/middle/user/password', user.UserPassword),
]
