from contextcrunch.strategies.article import ArticleRemovalStrategy


class TestArticleRemoval:
    def test_removes_article_in_instructional_context(self):
        s = ArticleRemovalStrategy()
        result, changes = s.apply("Create a function")
        assert "a" not in result.split()
        assert "function" in result

    def test_removes_the_in_instructional_context(self):
        s = ArticleRemovalStrategy()
        result, changes = s.apply("Delete the file")
        assert "the" not in result.split()
        assert "file" in result

    def test_preserves_the_with_being_verbs(self):
        s = ArticleRemovalStrategy()
        result, changes = s.apply("The system is running")
        assert "The" in result

    def test_preserves_articles_before_ordinals(self):
        s = ArticleRemovalStrategy()
        result, changes = s.apply("the first item")
        assert "the" in result
