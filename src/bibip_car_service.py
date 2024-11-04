from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
import os
from decimal import Decimal
from datetime import datetime
# from enum import StrEnum


class ModelIndex:
    def __init__(self, model_id: int, position_in_data_file: int):
        self.model_id = model_id
        self.position_in_data_file = position_in_data_file


class CarIndex:
    def __init__(self, car_id: str, position_in_data_file: int):
        self.car_id = car_id
        self.position_in_data_file = position_in_data_file


class SaleIndex:
    def __init__(self, sale_id: str, position_in_data_file: int):
        self.sale_id = sale_id
        self.position_in_data_file = position_in_data_file


class CarService:
    def __init__(self, root_dir: str) -> None:
        self.root_dir = root_dir

        self.model_index: list[ModelIndex] = []

        split_model_lines = self._read_file("models_index.txt")
        self.model_index = [ModelIndex(int(l[0]), int(l[1])) for l in split_model_lines]

        split_model_lines = self._read_file("cars_index.txt")
        self.car_index = [CarIndex(l[0], int(l[1])) for l in split_model_lines]

        split_model_lines = self._read_file("sales_index.txt")
        self.sale_index = [SaleIndex(l[0], int(l[1])) for l in split_model_lines]

    def _format_path(self, filename: str) -> str:
        return os.path.join(self.root_dir, filename)

    def _read_file(self, filename: str) -> list[list[str]]:
        if not os.path.exists(self._format_path(filename)):
            return []

        with open(self._format_path(filename), "r") as f:
            lines = f.readlines()
            split_lines = [l.strip().split(",") for l in lines]
            return split_lines

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        with open(self._format_path("models.txt"), "a") as f:
            str_model = f"{model.id},{model.name},{model.brand}".ljust(500)
            f.write(str_model + "\n")

        new_mi = ModelIndex(model.id, len(self.model_index))

        self.model_index.append(new_mi)
        self.model_index.sort(key=lambda x: x.model_id)
        f.close()

        with open(self._format_path("models_index.txt"), "w") as f:
            for current_mi in self.model_index:
                str_model = f"{current_mi.model_id},{current_mi.position_in_data_file}".ljust(50)
                f.write(str_model + "\n")
        f.close()

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        with open(self._format_path("cars.txt"), "a") as f:
            str_model = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
            f.write(str_model + "\n")

        new_ci = CarIndex(car.vin, len(self.car_index))

        self.car_index.append(new_ci)
        self.car_index.sort(key=lambda x: x.car_id)
        f.close()

        with open(self._format_path("cars_index.txt"), "w") as f:
            for current_ci in self.car_index:
                str_model = f"{current_ci.car_id},{current_ci.position_in_data_file}".ljust(50)
                f.write(str_model + "\n")
        f.close()

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        with open(self._format_path("sales.txt"), "a") as f:
            str_sale = f"{sale.sales_number},{sale.car_vin},{sale.sales_date},{sale.cost}".ljust(500)
            f.write(str_sale + "\n")

        new_si = SaleIndex(sale.car_vin, len(self.sale_index))

        self.sale_index.append(new_si)
        self.sale_index.sort(key=lambda x: x.sale_id)
        f.close()

        with open(self._format_path("sales_index.txt"), "w") as f:
            for current_si in self.sale_index:
                str_sale = f"{current_si.sale_id},{current_si.position_in_data_file}".ljust(50)
                f.write(str_sale + "\n")
        f.close()
        # Изменение статуса автомобиля
        with open(self._format_path("cars_index.txt"), "r") as file:
            car_strings: list[str] = file.readlines()
            target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id.strip() == sale.car_vin:
                    target_string = int(car_index)
                    break

            if target_string == -1:
                raise Exception("Car not found")

            with open(self._format_path("cars.txt"), "r+") as f:
                f.seek(target_string * 501)
                car_string = f.readline()
                car_arr = car_string.strip().split(",")
                car = Car(
                    vin=car_arr[0],
                    model=int(car_arr[1]),
                    price=Decimal(car_arr[2]),
                    date_start=datetime.strptime(car_arr[3], '%Y-%m-%d %H:%M:%S'),
                    status=CarStatus(car_arr[4]))

                car.status = CarStatus.sold

                f.seek(target_string * 501)
                car_line = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
                f.write(car_line + "\n")
            f.close()
        file.close()

        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        result = []
        with open(self._format_path("cars.txt"), "r") as file:
            lines = file.readlines()
            for line in lines:
                vin, model, price, date_start, car_status = line.strip().split(",")
                if car_status.strip() == status.value:
                    car = Car(
                        vin=vin,
                        model=int(model),
                        price=Decimal(price),
                        date_start=datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S'),
                        status=CarStatus(car_status.strip())
                    )
                    result.append(car)
        # С сотрировкой тест не проходит
        # result.sort(key=lambda car: car.vin)
        return result

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        with open(self._format_path("cars_index.txt"), "r") as file:
            car_strings: list[str] = file.readlines()
            target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    target_string = int(car_index)
                    break

            if target_string == -1:
                return None    # raise Exception("Car not found")

            with open(self._format_path("cars.txt"), "r") as f:
                f.seek(target_string * 501)
                car_string = f.readline()
                car_arr = car_string.strip().split(",")
                car = Car(
                    vin=car_arr[0],
                    model=int(car_arr[1]),
                    price=Decimal(car_arr[2]),
                    date_start=datetime.strptime(car_arr[3], '%Y-%m-%d %H:%M:%S'),
                    status=CarStatus(car_arr[4])
                    )
            f.close()
        file.close()
        ####
        with open(self._format_path("models_index.txt"), "r") as file:
            model_strings: list[str] = file.readlines()
            target_string = -1
            for model_string in model_strings:
                model_id, model_index = model_string.strip().split(",")
                if int(model_id) == car.model:
                    target_string = int(model_index)
                    break

            if target_string == -1:
                raise Exception("Model not found")

            with open(self._format_path("models.txt"), "r") as f:
                f.seek(target_string * 501)
                model_string = f.readline()
                model_arr = model_string.strip().split(",")
                model = Model(
                    id=int(model_arr[0]),
                    name=model_arr[1],
                    brand=model_arr[2]
                    )
            f.close()
        file.close()
        #
        if car.status == CarStatus.sold:
            with open(self._format_path("sales_index.txt"), "r") as file:
                sales_strings: list[str] = file.readlines()
                target_string = -1
                for sale_string in sales_strings:
                    sale_id, sale_index = sale_string.strip().split(",")
                    if sale_id == vin:
                        target_string = int(sale_index)
                        break

                if target_string == -1:
                    raise Exception("Car not found")

                with open(self._format_path("sales.txt"), "r") as f:
                    f.seek(target_string * 501)
                    sale_string = f.readline()
                    sale_arr = sale_string.strip().split(",")
                    sale = Sale(
                        sales_number=sale_arr[0],
                        car_vin=sale_arr[1],
                        sales_date=datetime.strptime(sale_arr[2], '%Y-%m-%d %H:%M:%S'),
                        cost=Decimal(sale_arr[3]),
                        )
                    sale_date = sale.sales_date
                    sale_price = sale.cost
                f.close()
            file.close()
        else:
            sale_price = None
            sale_date = None
        return CarFullInfo(
            vin=car.vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=car.price,
            date_start=car.date_start,
            status=car.status,
            sales_date=sale_date,
            sales_cost=sale_price
            )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        with open(self._format_path("cars_index.txt"), "r") as file:
            car_strings: list[str] = file.readlines()
            car_target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    car_target_string = int(car_index)    # Нашли vin
                    break

            if car_target_string == -1:    # Не нашли vin
                raise Exception("Car not found")
        file.close()

        with open(self._format_path("cars.txt"), "r+") as f:
            f.seek(car_target_string * 501)
            car_string = f.readline()
            car_arr = car_string.strip().split(",")
            car = Car(
                vin=new_vin,
                model=int(car_arr[1]),
                price=Decimal(car_arr[2]),
                date_start=datetime.strptime(car_arr[3], '%Y-%m-%d %H:%M:%S'),
                status=CarStatus(car_arr[4])
                )

            car_line = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
            f.seek(car_target_string * 501)
            f.write(car_line + "\n")
        f.close()
        result_car = car

        with open(self._format_path('cars.txt'), 'r') as file:
            cars_idx: list[tuple] = []
            for line_num, line in enumerate(file):
                car_arr = line.strip().split(',')
                car = Car(
                    vin=car_arr[0],
                    model=int(car_arr[1]),
                    price=Decimal(car_arr[2]),
                    date_start=datetime.strptime(car_arr[3], '%Y-%m-%d %H:%M:%S'),
                    status=CarStatus(car_arr[4])
                    )
                cars_idx.append((car.vin, line_num))

            cars_idx.sort(key=lambda x: x[0])
        file.close()

        with open(self._format_path('cars_index.txt'), 'w+') as file:
            for vin, line_num in cars_idx:
                idx_str = f'{vin},{line_num}'.ljust(50)
                file.write(idx_str + '\n')
        return result_car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        target_string = -1
        vin = None

        with open(self._format_path('sales.txt'), 'r') as f:
            for line_num, line in enumerate(f):
                sale_arr = line.strip().split(',')
                sale = Sale(
                    sales_number=sale_arr[0],
                    car_vin=sale_arr[1],
                    sales_date=datetime.strptime(sale_arr[2], '%Y-%m-%d %H:%M:%S'),
                    cost=Decimal(sale_arr[3]),
                    )
                if sale.sales_number == sales_number:
                    vin = sale.car_vin
                    target_string = line_num
                    break

        if target_string == -1:
            raise ValueError('Номер продажи не найден')
        f.close()
        #
        with open(self._format_path("cars_index.txt"), "r") as file:
            car_strings: list[str] = file.readlines()
            car_target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    car_target_string = int(car_index)    # Нашли vin
                    break

            if car_target_string == -1:    # Не нашли vin
                raise Exception("Car not found")

            with open(self._format_path("cars.txt"), "r+") as f:
                f.seek(car_target_string * 501)
                car_string = f.readline()
                car_arr = car_string.strip().split(",")
                car = Car(
                    vin=car_arr[0],
                    model=int(car_arr[1]),
                    price=Decimal(car_arr[2]),
                    date_start=datetime.strptime(car_arr[3], '%Y-%m-%d %H:%M:%S'),
                    status=CarStatus(car_arr[4]))

                car.status = CarStatus.available

                f.seek(car_target_string * 501)
                car_line = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
                f.write(car_line + "\n")
            f.close()
        file.close()

        with open(self._format_path('sales.txt'), 'r') as file:
            f_lines = file.readlines()
        file.close()
        with open(self._format_path('sales.txt'), 'w+') as file:
            for line_num, line in enumerate(f_lines):
                if line_num != target_string:
                    file.write(line)
        file.close()

        with open(self._format_path('sales.txt'), 'r') as file:
            sales_idx: list[tuple] = []
            for line_num, line in enumerate(file):
                sale_arr = line.strip().split(',')
                sale = Sale(
                    sales_number=sale_arr[0],
                    car_vin=sale_arr[1],
                    sales_date=datetime.strptime(sale_arr[2], '%Y-%m-%d %H:%M:%S'),
                    cost=Decimal(sale_arr[3]),
                    )
                sales_idx.append((sale.car_vin, line_num))

            sales_idx.sort(key=lambda x: x[0])
        file.close()

        with open(self._format_path('sales_index.txt'), 'w+') as file:
            for vin, line_num in sales_idx:
                idx_str = f'{vin},{line_num}'.ljust(50)
                file.write(idx_str + '\n')
        return car

    def get_car(self, vin: str):
        # Ищем в файле cars_index.txt нужный vin
        with open(self._format_path("cars_index.txt"), "r") as file:
            car_strings: list[str] = file.readlines()
            target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    target_string = int(car_index)    # Нашли vin
                    break

            if target_string == -1:    # Не нашли vin
                raise Exception("Car not found")
            # Ищем по найденному vin авто в файле cars.txt
            with open(self._format_path("cars.txt"), "r") as f:
                f.seek(target_string * 501)
                car_string = f.readline()
                car_arr = car_string.strip().split(",")
                car = Car(    # Нашли авто и создали объект car
                    vin=car_arr[0],
                    model=int(car_arr[1]),
                    price=Decimal(car_arr[2]),
                    date_start=datetime.strptime(car_arr[3], '%Y-%m-%d %H:%M:%S'),
                    status=CarStatus(car_arr[4])
                    )
            f.close()
        file.close()
        return car

    def get_model(self, id: int):
        with open(self._format_path("models_index.txt"), "r") as file:
            model_strings: list[str] = file.readlines()
            target_string = -1
            for model_string in model_strings:
                model_id, model_index = model_string.strip().split(",")
                if int(model_id) == id:
                    target_string = int(model_index)    # Нашли id модели
                    break

            if target_string == -1:    # Не нашли id
                raise Exception("Model not found")
            # Ищем по найденному id саму модель
            with open(self._format_path("models.txt"), "r") as f:
                f.seek(target_string * 501)
                model_string = f.readline()
                model_arr = model_string.strip().split(",")
                model = Model(    # Нашли модель и создали объект model
                    id=int(model_arr[0]),
                    name=model_arr[1],
                    brand=model_arr[2]
                    )
            f.close()
        file.close()
        return model

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # Заводим словарь ключ - id модели, значение - кол-во продаж
        model_sales: dict[int, int] = {}
        # Читаем файл sales построчно
        i = 0
        with open(self._format_path("sales.txt"), "r") as file:
            for line in file:
                i += 1
                # Для каждой строчки
                # берем id модели и инкрементируем значение в словаре
                sale_arr = line.strip().split(",")
                sale = Sale(
                    sales_number=sale_arr[0],
                    car_vin=sale_arr[1],
                    sales_date=datetime.strptime(sale_arr[2], '%Y-%m-%d %H:%M:%S'),
                    cost=Decimal(sale_arr[3]),
                    )
                car = self.get_car(sale.car_vin)
                if car.model in model_sales:
                    model_sales[car.model] += 1    # Считаем продажи
                else:
                    model_sales[car.model] = 1
        # Сортируем словарь по значениям
        top_models = sorted(model_sales.items(), key=lambda item: item[1], reverse=True)[0:3]
        model_sales = dict(top_models)
        model_stats: list[ModelSaleStats] = []    # Итоговый результат
        ###
        # Собираем данные из models.txt и словаря
        # находим модель по car_vin
        for key, value in model_sales.items():
            model = self.get_model(key)
            model_stats.append(ModelSaleStats(
                    car_model_name=model.name,
                    brand=model.brand,
                    sales_number=value)
                    )
        return model_stats

""" Проверка работы функций
if __name__ == '__main__':
    obj = CarService("/Users/lina/Dev/InterimProject/de-project-bibip/temp_data")
    ''' Заполнение файлов с моделями и индексами (Задание 1)
    model_1 = Model(id=1, name="Optima", brand="Kia")
    model_2 = Model(id=2, name="Sorento", brand="Kia")
    model_3 = Model(id=3, name="3", brand="Mazda")
    model_4 = Model(id=4, name="Pathfinder", brand="Nissan")
    model_5 = Model(id=5, name="Logan", brand="Renault")
    obj.add_model(model_1)
    obj.add_model(model_2)
    obj.add_model(model_3)
    obj.add_model(model_4)
    obj.add_model(model_5)
    '''
    # Проверка ф-ции get_model()
    # print(obj.get_model(4))
    ''' Заполнение файлов с машинами и индексами (Задание 1)
    car_1 = Car(
            vin="KNAGM4A77D5316538",
            model=1,
            price=Decimal("2000"),
            date_start=datetime(2024, 2, 8),
            status=CarStatus.available
        )
    car_2 = Car(
            vin="5XYPH4A10GG021831",
            model=2,
            price=Decimal("2300"),
            date_start=datetime(2024, 2, 20),
            status=CarStatus.reserve
        )
    car_3 = Car(
            vin="KNAGH4A48A5414970",
            model=1,
            price=Decimal("2100"),
            date_start=datetime(2024, 4, 4),
            status=CarStatus.available
        )
    car_4 = Car(
            vin="JM1BL1TFXD1734246",
            model=3,
            price=Decimal("2276.65"),
            date_start=datetime(2024, 5, 17),
            status=CarStatus.available
        )
    car_5 = Car(
            vin="JM1BL1M58C1614725",
            model=3,
            price=Decimal("2549.10"),
            date_start=datetime(2024, 5, 17),
            status=CarStatus.reserve
        )
    car_6 = Car(
            vin="KNAGR4A63D5359556",
            model=1,
            price=Decimal("2376"),
            date_start=datetime(2024, 5, 17),
            status=CarStatus.available
        )
    car_7 = Car(
            vin="5N1CR2MN9EC641864",
            model=4,
            price=Decimal("3100"),
            date_start=datetime(2024, 6, 1),
            status=CarStatus.available
        )
    car_8 = Car(
            vin="JM1BL1L83C1660152",
            model=3,
            price=Decimal("2635.17"),
            date_start=datetime(2024, 6, 1),
            status=CarStatus.available
        )
    car_9 = Car(
            vin="5N1CR2TS0HW037674",
            model=4,
            price=Decimal("3100"),
            date_start=datetime(2024, 6, 1),
            status=CarStatus.available
        )
    car_10 = Car(
            vin="5N1AR2MM4DC605884",
            model=4,
            price=Decimal("3200"),
            date_start=datetime(2024, 7, 15),
            status=CarStatus.available
        )
    car_11 = Car(
            vin="VF1LZL2T4BC242298",
            model=5,
            price=Decimal("2280.76"),
            date_start=datetime(2024, 8, 31),
            status=CarStatus.delivery
        )
    obj.add_car(car_1)
    obj.add_car(car_2)
    obj.add_car(car_3)
    obj.add_car(car_4)
    obj.add_car(car_5)
    obj.add_car(car_6)
    obj.add_car(car_7)
    obj.add_car(car_8)
    obj.add_car(car_9)
    obj.add_car(car_10)
    obj.add_car(car_11)
    '''

    # obj.update_vin("VF1LZVF1LZL2T4BC242298", "VF1LZL2T4BC242298")

    ''' Тестила функцию get_model_info()    # ОНА НЕ НУЖНА???
    # obj.get_model_info("VF1LZL2T4BC242298")
    # model_5 = obj.get_model_info("VF1LZL2T4BC242298")
    # print(model_5)
    '''
    '''
    sale = Sale(
        sales_number="20240903#JM1BL1M58C1614725",
        car_vin="JM1BL1M58C1614725",
        sales_date=datetime(2024, 9, 3),
        cost=Decimal("2399.99")
    )
    obj.sell_car(sale)
    '''
    # Проверка работы ф-ции get_car()
    # print(obj.get_car("5N1CR2TS0HW037674"))

    ''' Заполнение продаж
    # Для 7 Задания и проверка работы 2 Задане (Заполнение продаж)
    sale_1 = Sale(
        sales_number="20240903#KNAGM4A77D5316538",
        car_vin="KNAGM4A77D5316538",
        sales_date=datetime(2024, 9, 3),
        cost=Decimal("1999.09")
    )
    sale_2 = Sale(
        sales_number="20240903#KNAGH4A48A5414970",
        car_vin="KNAGH4A48A5414970",
        sales_date=datetime(2024, 9, 4),
        cost=Decimal("2100")
    )
    sale_3 = Sale(
        sales_number="20240903#KNAGR4A63D5359556",
        car_vin="KNAGR4A63D5359556",
        sales_date=datetime(2024, 9, 5),
        cost=Decimal("7623")
    )
    sale_4 = Sale(
        sales_number="20240903#JM1BL1M58C1614725",
        car_vin="JM1BL1M58C1614725",
        sales_date=datetime(2024, 9, 6),
        cost=Decimal("2334")
    )
    sale_5 = Sale(
        sales_number="20240903#JM1BL1L83C1660152",
        car_vin="JM1BL1L83C1660152",
        sales_date=datetime(2024, 9, 7),
        cost=Decimal("451")
    )
    sale_6 = Sale(
        sales_number="20240903#5N1CR2TS0HW037674",
        car_vin="5N1CR2TS0HW037674",
        sales_date=datetime(2024, 9, 8),
        cost=Decimal("9876")
    )
    sale_7 = Sale(
        sales_number="20240903#5XYPH4A10GG021831",
        car_vin="5XYPH4A10GG021831",
        sales_date=datetime(2024, 9, 9),
        cost=Decimal("1234")
    )
    obj.sell_car(sale_1)
    obj.sell_car(sale_2)
    obj.sell_car(sale_3)
    obj.sell_car(sale_4)
    obj.sell_car(sale_5)
    obj.sell_car(sale_6)
    obj.sell_car(sale_7)
    '''
    # Задание 6
    # obj.revert_sale("20240903#5N1CR2TS0HW037674")
    # Задание 3
    # print(obj.get_cars(CarStatus.available))
    # Задание 4
    # print(obj.get_car_info("VF1LZL2T4BC242298"))
    ''' Проверка топ-3 (7 Задание)
    print('--------------------------------------------------')
    print(obj.top_models_by_sales())    # Без sales не получится
    # obj.top_models_by_sales()
    print('--------------------------------------------------')
    '''
""" 