#include <iostream>
#include <iomanip>
#include <cmath>
#include <limits>
#include <string>

using namespace std;

// Прототипы функций
void show_menu();
void get_user_input_and_calculate();
void calculate_turnover(double revenue, double avg_assets, 
                       double equity_capital, double debt_capital,
                       int period_days = 365);
double get_positive_input(const string& prompt, double min_val, double max_val);
void test_calculation();
string interpret_turnover(double turnover);

int main() {
    int choice;
    
    while (true) {
        show_menu();
        
        if (cin >> choice) {
            if (choice == 1) {
                get_user_input_and_calculate();
            } 
            else if (choice == 2) {
                test_calculation();
            } 
            else if (choice == 3) {
                cout << "\nВыход из программы. До свидания!\n";
                return 0;
            } 
            else {
                cout << "Ошибка: введите число от 1 до 3\n";
            }
        } 
        else {
            cout << "Ошибка: введите числовое значение\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
    }
}

void show_menu() {
    cout << "\n";
    cout << "========================================\n";
    cout << "   СИСТЕМА РАСЧЕТА ПОКАЗАТЕЛЕЙ         \n";
    cout << "   ОБОРАЧИВАЕМОСТИ КАПИТАЛА            \n";
    cout << "========================================\n";
    cout << "1. Выполнение (ввод данных и расчет)   \n";
    cout << "2. Тестирование (автоматические тесты) \n";
    cout << "3. Выход из программы                  \n";
    cout << "========================================\n";
    cout << "Выберите действие (1-3): ";
}

double get_positive_input(const string& prompt, double min_val, double max_val) {
    double value;
    while (true) {
        cout << prompt;
        if (cin >> value) {
            if (value >= min_val && value <= max_val) {
                return value;
            } else {
                cout << "Ошибка: значение должно быть от " << min_val << " до " << max_val << "\n";
            }
        } else {
            cout << "Ошибка: введите числовое значение\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
    }
}

void get_user_input_and_calculate() {
    double revenue, avg_assets, equity_capital, debt_capital;
    int period_days;
    
    cout << "\n=== ВВОД ФИНАНСОВЫХ ДАННЫХ ===\n";
    
    // Ввод выручки
    revenue = get_positive_input("Введите выручку от продаж (0 - 10^12): ", 0, 1e12);
    
    // Ввод среднегодовых активов
    while (true) {
        avg_assets = get_positive_input("Введите среднегодовую стоимость активов (0.01 - 10^12): ", 0.01, 1e12);
        if (avg_assets >= 0.01) {
            break;
        }
        cout << "Ошибка: активы должны быть не менее 0.01\n";
    }
    
    // Ввод собственного капитала
    equity_capital = get_positive_input("Введите собственный капитал (0 - 10^12): ", 0, 1e12);
    
    // Ввод заемного капитала
    debt_capital = get_positive_input("Введите заемный капитал (0 - 10^12): ", 0, 1e12);
    
    // Ввод периода для расчета
    while (true) {
        cout << "Введите период для расчета (1-366 дней, по умолчанию 365): ";
        if (cin >> period_days) {
            if (period_days >= 1 && period_days <= 366) {
                break;
            } else {
                cout << "Ошибка: период должен быть от 1 до 366 дней\n";
            }
        } else {
            // Если ввод пустой, используем значение по умолчанию
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            period_days = 365;
            break;
        }
    }
    
    cout << "\n=== ВЫПОЛНЕНИЕ РАСЧЕТОВ ===\n";
    calculate_turnover(revenue, avg_assets, equity_capital, debt_capital, period_days);
}

string interpret_turnover(double turnover) {
    if (turnover > 2.0) {
        return "высокая оборачиваемость";
    } else if (turnover > 1.0) {
        return "средняя оборачиваемость";
    } else {
        return "низкая оборачиваемость";
    }
}

void calculate_turnover(double revenue, double avg_assets, 
                       double equity_capital, double debt_capital,
                       int period_days) {
    
    // Проверка входных данных
    if (revenue < 0 || revenue > 1e12) {
        cout << "Ошибка: выручка должна быть в диапазоне от 0 до 10^12\n";
        return;
    }
    
    if (avg_assets < 0.01 || avg_assets > 1e12) {
        cout << "Ошибка: среднегодовые активы должны быть в диапазоне от 0.01 до 10^12\n";
        return;
    }
    
    if (equity_capital < 0 || equity_capital > 1e12) {
        cout << "Ошибка: собственный капитал должен быть в диапазоне от 0 до 10^12\n";
        return;
    }
    
    if (debt_capital < 0 || debt_capital > 1e12) {
        cout << "Ошибка: заемный капитал должен быть в диапазоне от 0 до 10^12\n";
        return;
    }
    
    if (period_days < 1 || period_days > 366) {
        cout << "Ошибка: период должен быть от 1 до 366 дней\n";
        return;
    }
    
    // Расчет коэффициентов оборачиваемости
    double asset_turnover = 0.0;
    if (avg_assets > 0) {
        asset_turnover = revenue / avg_assets;
    }
    
    double equity_turnover = 0.0;
    if (equity_capital > 0) {
        equity_turnover = revenue / equity_capital;
    }
    
    double debt_turnover = 0.0;
    if (debt_capital > 0) {
        debt_turnover = revenue / debt_capital;
    }
    
    // Расчет периода оборота
    double turnover_period = 0.0;
    if (asset_turnover > 0) {
        turnover_period = static_cast<double>(period_days) / asset_turnover;
    }
    
    // Вывод результатов
    cout << fixed << setprecision(1);
    cout << "\n=== РЕЗУЛЬТАТЫ РАСЧЕТА ===\n\n";
    
    cout << "Оборачиваемость активов: " << asset_turnover << endl;
    
    if (equity_turnover > 0) {
        cout << "Оборачиваемость собственного капитала: " << equity_turnover << endl;
    } else {
        cout << "Оборачиваемость собственного капитала: не рассчитывается (СК = 0)\n";
    }
    
    if (debt_turnover > 0) {
        cout << "Оборачиваемость заемного капитала: " << debt_turnover << endl;
    } else {
        cout << "Оборачиваемость заемного капитала: не рассчитывается (ЗК = 0)\n";
    }
    
    cout << fixed << setprecision(1);
    if (turnover_period > 0) {
        cout << "Период оборота: " << turnover_period << " дней\n";
    } else {
        cout << "Период оборота: не рассчитывается\n";
    }
    
    // Сравнение с отраслевыми нормативами
    cout << "\n=== АНАЛИЗ РЕЗУЛЬТАТОВ ===\n";
    
    cout << "• Оборачиваемость активов: " << interpret_turnover(asset_turnover) << endl;
    
    if (equity_turnover > 0) {
        cout << "• Оборачиваемость собственного капитала: " << interpret_turnover(equity_turnover) << endl;
    }
    
    if (debt_turnover > 0) {
        cout << "• Оборачиваемость заемного капитала: " << interpret_turnover(debt_turnover) << endl;
    }
    
    // Анализ динамики
    cout << "\n• Для анализа динамики необходимы данные за предыдущие периоды" << endl;
    cout << "• Рекомендуется отслеживать изменение показателей во времени" << endl;
    cout << "• Сравните с отраслевыми нормативами для вашей сферы деятельности" << endl;
    
    cout << "\n========================================\n";
}

void test_calculation() {
    cout << "\n=== АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ===\n\n";
    
    cout << "Тест 1: Пример 1 из задания (выручка 2 млн)\n";
    cout << "-------------------------------------------\n";
    calculate_turnover(2000000, 1000000, 500000, 300000, 365);
    
    cout << "\nТест 2: Пример 2 из задания (выручка 1 млн)\n";
    cout << "-------------------------------------------\n";
    calculate_turnover(1000000, 600000, 300000, 150000, 365);
    
    cout << "\nТест 3: Нулевой заемный капитал\n";
    cout << "--------------------------------\n";
    calculate_turnover(1000000, 500000, 400000, 0, 365);
    
    cout << "\nТест 4: Нулевой собственный капитал\n";
    cout << "------------------------------------\n";
    calculate_turnover(1000000, 500000, 0, 400000, 365);
    
    cout << "\nТест 5: Высокая оборачиваемость\n";
    cout << "-------------------------------\n";
    calculate_turnover(5000000, 1000000, 2000000, 500000, 365);
    
    cout << "\nТест 6: Низкая оборачиваемость\n";
    cout << "------------------------------\n";
    calculate_turnover(500000, 1000000, 800000, 200000, 365);
    
    cout << "\nТест 7: Ошибка - нулевые активы\n";
    cout << "-------------------------------\n";
    calculate_turnover(1000000, 0, 500000, 300000, 365);
    
    cout << "\nТест 8: Ошибка - отрицательная выручка\n";
    cout << "--------------------------------------\n";
    calculate_turnover(-1000000, 500000, 300000, 200000, 365);
    
    cout << "\nТест 9: Другой период (90 дней)\n";
    cout << "--------------------------------\n";
    calculate_turnover(1000000, 500000, 300000, 200000, 90);
    
    cout << "\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===\n";
}
