import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramUnauthorizedError
from .. import loader, utils
from typing import Optional

logger = logging.getLogger(__name__)

@loader.tds
class CapitalTurnoverMod(loader.Module):
    """Модуль расчета оборачиваемости капитала - Рафиков Роман, УИБO-14-24"""
    
    strings = {
        "name": "КапиталОборот",
        "menu_text": (
            "📊 <b>Расчет оборачиваемости капитала</b>\n\n"
            "<i>Курсовая работа</i>\n"
            "<b>Рафиков Роман, УИБO-14-24</b>\n\n"
            "Выберите действие:"
        ),
        "calculate_button": "🧮 Сделать расчет",
        "test_button": "📋 Примеры из задания",
        "back_button": "🔙 Назад",
        "calculate_text": (
            "🧮 <b>Введите данные для расчета</b>\n\n"
            "<b>Формат команды:</b>\n"
            "<code>.calculate выручка активы собственный_капитал заемный_капитал</code>\n\n"
            "<i>период в днях - необязательно, по умолчанию 365</i>\n\n"
            "<b>Примеры:</b>\n"
            "<code>.calculate 2000000 1000000 500000 300000</code>\n"
            "<code>.calculate 1000000 600000 300000 150000 365</code>\n\n"
            "<b>Что рассчитывается:</b>\n"
            "• Оборачиваемость активов = выручка ÷ активы\n"
            "• Оборачиваемость СК = выручка ÷ собственный капитал\n"
            "• Оборачиваемость ЗК = выручка ÷ заемный капитал\n"
            "• Период оборота = дни ÷ оборачиваемость активов\n\n"
            "<b>Примечание:</b> В примерах из задания вероятно допущена ошибка в расчете оборачиваемости заемного капитала.\n"
            "⚠️ <i>В примере 1: в задании указано 3.3, но по расчету выходит 6.7</i>\n"
            "⚠️ <i>В примере 2: в задании указано 2.0, но по расчету выходит 6.7</i>\n\n"
        ),
        "test_text": (
            "📋 <b>Примеры из задания</b>\n\n"
            "Выберите пример для проверки:"
        ),
        "invalid_input": "❌ <b>Неверный формат!</b>\n\nИспользуйте: <code>.calculate 2000000 1000000 500000 300000</code>",
        "input_error": "❌ <b>Ошибка</b>\n\n{error}",
        "calculation_results": "📈 <b>Результаты расчета</b>\n\n{results}",
        "test_results": "📋 <b>Результат проверки</b>\n\n{results}",
        "test_example_1": "📄 Пример 1",
        "test_example_2": "📄 Пример 2",
        "test_my_data": "📝 Мой расчет",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "BOT_TOKEN",
                None,
                lambda: "Токен бота",
                validator=loader.validators.String(),
            ),
        )
        self._support_bot = None
        self._client = None
        self._me = None
        self.user_data = {}
        self.last_calculation = {}

    async def client_ready(self, client, db):
        self._client = client
        self._me = await client.get_me()
        logger.info(f"Модуль расчета капитала загружен")

    def _interpret_turnover(self, turnover: float) -> str:
        if turnover > 2.0:
            return "высокая"
        elif turnover > 1.0:
            return "средняя"
        else:
            return "низкая"

    def _calculate_turnover(self, revenue: float, avg_assets: float, 
                           equity_capital: float, debt_capital: float,
                           period_days: int = 365) -> dict:
        
        results = {
            "success": True,
            "errors": [],
            "asset_turnover": 0.0,
            "equity_turnover": 0.0,
            "debt_turnover": 0.0,
            "turnover_period": 0.0,
            "messages": []
        }
        
        # Проверки данных
        if revenue < 0 or revenue > 1e12:
            results["success"] = False
            results["errors"].append("Выручка: от 0 до 10^12")
        
        if avg_assets < 0.01 or avg_assets > 1e12:
            results["success"] = False
            results["errors"].append("Активы: от 0.01 до 10^12")
        
        if equity_capital < 0 or equity_capital > 1e12:
            results["success"] = False
            results["errors"].append("Собственный капитал: от 0 до 10^12")
        
        if debt_capital < 0 or debt_capital > 1e12:
            results["success"] = False
            results["errors"].append("Заемный капитал: от 0 до 10^12")
        
        if period_days < 1 or period_days > 366:
            results["success"] = False
            results["errors"].append("Период: 1-366 дней")
        
        if not results["success"]:
            return results
        
        # Расчет показателей
        if avg_assets > 0:
            results["asset_turnover"] = revenue / avg_assets
        
        if equity_capital > 0:
            results["equity_turnover"] = revenue / equity_capital
        
        if debt_capital > 0:
            results["debt_turnover"] = revenue / debt_capital
        
        if results["asset_turnover"] > 0:
            results["turnover_period"] = period_days / results["asset_turnover"]
        
        # Форматирование результатов
        results["messages"].append(f"<b>Оборачиваемость активов:</b> {results['asset_turnover']:.1f}")
        
        if equity_capital > 0:
            results["messages"].append(f"<b>Оборачиваемость собственного капитала:</b> {results['equity_turnover']:.1f}")
        else:
            results["messages"].append("<b>Оборачиваемость собственного капитала:</b> (не рассчитывается, СК = 0)")
        
        if debt_capital > 0:
            results["messages"].append(f"<b>Оборачиваемость заемного капитала:</b> {results['debt_turnover']:.1f}")
            
            # Проверка на примеры из задания
            if abs(revenue - 2000000) < 0.1 and abs(debt_capital - 300000) < 0.1:
                results["messages"].append("⚠️ <i>В задании указано 3.3, но по расчету выходит 6.7</i>")
            elif abs(revenue - 1000000) < 0.1 and abs(debt_capital - 150000) < 0.1:
                results["messages"].append("⚠️ <i>В задании указано 2.0, но по расчету выходит 6.7</i>")
        else:
            results["messages"].append("<b>Оборачиваемость заемного капитала:</b> (не рассчитывается, ЗК = 0)")
        
        if results["turnover_period"] > 0:
            results["messages"].append(f"<b>Период оборота:</b> {results['turnover_period']:.1f} дней")
        else:
            results["messages"].append("<b>Период оборота:</b> (не рассчитывается)")
        
        # Анализ результатов
        results["messages"].append(f"\n📊 <b>Анализ:</b>")
        results["messages"].append(f"• Активы: {self._interpret_turnover(results['asset_turnover'])} оборачиваемость")
        
        if equity_capital > 0:
            results["messages"].append(f"• Собственный капитал: {self._interpret_turnover(results['equity_turnover'])} оборачиваемость")
        
        if debt_capital > 0:
            results["messages"].append(f"• Заемный капитал: {self._interpret_turnover(results['debt_turnover'])} оборачиваемость")
        
        return results

    async def calculatecmd(self, message):
        """Главная команда - работает как меню или сразу делает расчет"""
        args = utils.get_args_raw(message)
        
        # Если аргументов нет - показываем меню
        if not args:
            await self._show_main_menu(message)
            return
        
        # Если есть аргументы - делаем расчет
        try:
            parts = args.split()
            
            if len(parts) < 4 or len(parts) > 5:
                await utils.answer(message, self.strings["invalid_input"])
                return
            
            # Конвертируем числа
            numbers = []
            for part in parts:
                clean_part = part.replace(',', '.')
                try:
                    num = float(clean_part)
                    numbers.append(num)
                except:
                    await utils.answer(message, self.strings["invalid_input"])
                    return
            
            # Извлекаем данные
            revenue = numbers[0]
            avg_assets = numbers[1]
            equity_capital = numbers[2]
            debt_capital = numbers[3]
            period_days = numbers[4] if len(numbers) > 4 else 365
            
            # Проверка периода
            if period_days < 1 or period_days > 366:
                await utils.answer(
                    message,
                    self.strings["input_error"].format(error="Период должен быть от 1 до 366 дней")
                )
                return
            
            # Делаем расчет
            results = self._calculate_turnover(
                revenue, avg_assets, equity_capital, debt_capital, period_days
            )
            
            if not results["success"]:
                error_text = "❌ <b>Ошибки в данных:</b>\n"
                error_text += "\n".join(results["errors"])
                await utils.answer(message, error_text)
                return
            
            # Формируем результат
            result_text = "✅ <b>Расчет завершен</b>\n\n"
            result_text += "\n".join(results["messages"])
            
            # Сохраняем для истории
            user_id = message.sender_id
            self.last_calculation[user_id] = {
                "revenue": revenue,
                "avg_assets": avg_assets,
                "equity_capital": equity_capital,
                "debt_capital": debt_capital,
                "period_days": period_days,
                "results": results
            }
            
            # Показываем результат с кнопками
            await self.inline.form(
                message=message,
                text=result_text,
                reply_markup=[
                    [{"text": "🔄 Новый расчет", "callback": self._show_calculate_menu}],
                    [{"text": "📋 Примеры", "callback": self._show_test_menu}]
                ],
                ttl=60*60*24
            )
            
        except Exception as e:
            logger.error(f"Ошибка в calculatecmd: {e}")
            await utils.answer(
                message,
                self.strings["input_error"].format(error="Проверьте правильность ввода чисел")
            )

    async def _show_main_menu(self, message):
        """Показать главное меню"""
        buttons = [
            [
                {"text": self.strings["calculate_button"], "callback": self._show_calculate_menu}
            ],
            [
                {"text": self.strings["test_button"], "callback": self._show_test_menu}
            ]
        ]
        
        await self.inline.form(
            message=message,
            text=self.strings["menu_text"],
            reply_markup=buttons,
            ttl=60*60*24
        )

    async def _show_calculate_menu(self, call):
        """Показать инструкцию для ввода данных"""
        await call.edit(
            self.strings["calculate_text"],
            reply_markup=[
                [{"text": self.strings["back_button"], "callback": self._back_to_menu}]
            ]
        )

    async def _show_test_menu(self, call):
        """Показать меню с примерами"""
        buttons = [
            [
                {"text": self.strings["test_example_1"], "callback": self._run_test_1},
                {"text": self.strings["test_example_2"], "callback": self._run_test_2}
            ],
            [
                {"text": self.strings["test_my_data"], "callback": self._show_my_test}
            ],
            [
                {"text": self.strings["back_button"], "callback": self._back_to_menu}
            ]
        ]
        
        await call.edit(
            self.strings["test_text"],
            reply_markup=buttons
        )

    async def _back_to_menu(self, call):
        """Вернуться в главное меню"""
        buttons = [
            [
                {"text": self.strings["calculate_button"], "callback": self._show_calculate_menu}
            ],
            [
                {"text": self.strings["test_button"], "callback": self._show_test_menu}
            ]
        ]
        
        await call.edit(
            self.strings["menu_text"],
            reply_markup=buttons
        )

    async def _run_test_1(self, call):
        """Запустить тест 1 (пример из задания)"""
        results = self._calculate_turnover(2000000, 1000000, 500000, 300000, 365)
        await self._show_test_results(call, "📄 Пример 1 из задания", results)

    async def _run_test_2(self, call):
        """Запустить тест 2 (пример из задания)"""
        results = self._calculate_turnover(1000000, 600000, 300000, 150000, 365)
        await self._show_test_results(call, "📄 Пример 2 из задания", results)

    async def _show_my_test(self, call):
        """Тест с пользовательскими данными"""
        user_id = call.from_user.id
        
        if user_id in self.last_calculation:
            data = self.last_calculation[user_id]
            results = self._calculate_turnover(
                data["revenue"], 
                data["avg_assets"], 
                data["equity_capital"], 
                data["debt_capital"], 
                data["period_days"]
            )
            await self._show_test_results(call, "📝 Мой последний расчет", results)
        else:
            await call.answer("❌ Сначала выполните расчет", show_alert=True)

    async def _show_test_results(self, call, test_name: str, results: dict):
        """Показать результаты теста"""
        if not results["success"]:
            error_text = f"❌ <b>{test_name}</b>\n\n"
            error_text += "\n".join(results["errors"])
            
            await call.edit(
                error_text,
                reply_markup=[
                    [{"text": "🔙 Назад к примерам", "callback": self._show_test_menu}],
                    [{"text": "🏠 В меню", "callback": self._back_to_menu}]
                ]
            )
            return
        
        result_text = f"📋 <b>{test_name}</b>\n\n"
        result_text += "\n".join(results["messages"])
        
        await call.edit(
            result_text,
            reply_markup=[
                [{"text": "🔙 Назад к примерам", "callback": self._show_test_menu}],
                [{"text": "🏠 В меню", "callback": self._back_to_menu}]
            ]
        )

    async def watcher(self, message):
        """Обработчик сообщений для режима ввода данных"""
        try:
            if not message or not hasattr(message, 'is_private') or not message.is_private:
                return
            
            if not hasattr(message, 'sender_id') or message.sender_id == getattr(self._me, 'id', None):
                return
            
            text = getattr(message, 'text', '').strip()
            
            # Если пользователь в режиме ввода данных
            user_id = message.sender_id
            if user_id in self.user_data and self.user_data[user_id].get("waiting_for_input", False):
                # Убираем флаг ожидания
                self.user_data[user_id]["waiting_for_input"] = False
                
                # Обрабатываем ввод
                try:
                    parts = text.split()
                    
                    if len(parts) < 4 or len(parts) > 5:
                        await utils.answer(message, self.strings["invalid_input"])
                        return
                    
                    # Формируем команду
                    cmd_args = " ".join(parts)
                    fake_message = type('obj', (object,), {
                        'sender_id': user_id,
                        'text': f".calculate {cmd_args}",
                        'reply': None
                    })()
                    
                    await self.calculatecmd(fake_message)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки ввода: {e}")
                    await utils.answer(message, self.strings["invalid_input"])
                
        except Exception as e:
            logger.error(f"Ошибка в watcher: {e}")

    async def on_unload(self):
        """Очистка при выгрузке модуля"""
        self.user_data.clear()
        self.last_calculation.clear()
