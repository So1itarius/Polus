import unittest

def handler_from_http(x):
    return x.replace("<h2>\n\t\t\t<span>", "").replace("</span> ", " ").replace("\n\t\t\t", "").replace(" \n\t\t","").replace("</h2>", "")


class Unittest(unittest.TestCase):

    def test_handler_from_http(self):
        example1 = '<h2>\n\t\t\t<span>[PRC-2018-0079]</span> \n\t\t\tПроведение периодического медицинского осмотра работников АО «Полюс Вернинское» [этап 3] \n\t\t</h2>'
        example2 = '<h2>\n\t\t\t<span>[PG-2018-0096]</span> \n\t\t\tКанал Красноярск - Москва 1 Гбит \n\t\t</h2>'
        result = handler_from_http(example1)
        result2 = handler_from_http(example2)
        self.assertEqual('[PRC-2018-0079] Проведение периодического медицинского осмотра работников АО «Полюс Вернинское» [этап 3]', result)
        self.assertEqual(
            '[PG-2018-0096] Канал Красноярск - Москва 1 Гбит',
            result2)

