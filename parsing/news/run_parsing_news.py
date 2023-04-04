import sys

sys.path.append("/api")

from parsing.parsers.news_parser import NewsParser

if __name__ == '__main__':
    news_parser = NewsParser()
    news_parser.start_parse_news()
