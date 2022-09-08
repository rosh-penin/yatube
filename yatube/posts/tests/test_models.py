from .constants import TestBase
from posts.constants import CUT_STR_POST


class ModelTests(TestBase):

    def test_check_str(self):
        with self.subTest(name="post"):
            self.assertEqual(str(self.post), self.post.text[:CUT_STR_POST])
        with self.subTest(name="group"):
            self.assertEqual(str(self.group), self.group.title)
