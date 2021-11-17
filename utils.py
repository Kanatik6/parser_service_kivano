import requests
from bs4 import BeautifulSoup as BS
from .models import Notebook

def html_soup(url=None):
    response = requests.get(url)
    soup = BS(response.content,'html.parser')
    return soup

class ParserServiceKivano:
    url = 'https://www.kivano.kg/'
        
    # * этот метод принимает суп и возвращает последнюю страницу 
    def find_last(self,html):
        last = html.find('li',class_='last')
        print(last.get_text(strip=True))
        return int(last.get_text(strip=True))
    
    # * принимает название категории и возвращает список страниц
    def get_full_pages(self,category):
        url = self.url+category
        final_pages = url.join(f'?page={i}|'for i in range(0,self.find_last(html_soup(category))+1))
        # * эта строка только потому что html страницы 
        final_pages = final_pages.split('|')[1:-1]
        return final_pages
    
    
    def parse(self,list_of_pages):
        # * в эту переменную записываю айдишки продуктов что пройдут проверку
        id_list = list()
        
        # * по 1 url из списка url'ов
        for url in list_of_pages:
            print(url)
            html = html_soup(url=url)
            
            list_ = html.find('div', class_='list-view')
            items = list_.find_all('div',class_='item product_listbox oh')
            
            for i in items:
                
                title = i.find('div',class_='listbox_title oh').get_text(strip=True)
                price = i.find('div',class_='listbox_price text-center').get_text(strip=True)
                
                # * url от списка продуктов к одному продукту
                href = self.url.rstrip('/') +i.find('div',class_='listbox_title oh').find('strong').find('a').get('href')
                html = html_soup(url=href)
                
                # * в этой переменной я храню таблицу информации
                table = html.find('div',class_='tab-pane fade in active yandex_hide_some',id='desc')
                attributes = table.text.split('\n')
                
                # * эта строчка нужна чтобы убрать вечные плавающие пустые элементы списка 
                attributes = [i for i in attributes if i !='']
                
                # * в эту переменную записываю весь результат парса
                res_dict = dict()
                
                # * тут вытаскиваем построчно из таблицы информации
                for line in attributes:
                    # * тут пропускается в случае если нельзя разделить по : значит нет нужной инфы 
                    try:
                        a = line.split(':')
                        res_dict[a[0]] =a[1].strip()
                    except Exception:
                        continue
                    
                    
                # * вытаскиваю переменные
                os = res_dict.get('Операционная система', 'Не указано')
                cpu = res_dict.get('Процессор', 'Не указано')
                frequency = res_dict.get('Частота', 'Не указано')
                cores = res_dict.get('Количество ядер', 'Не указано')
                diagonal = res_dict.get('Диагональ экрана', 'Не указано')
                screen_resolution = res_dict.get('Разрешение экрана', 'Не указано')
                ram = res_dict.get('Объем оперативной памяти', 'Не указано')
                drive_type = res_dict.get('Тип накопителя', 'Не указано')
                if drive_type == 'SSD':
                    storage_volume = res_dict.get('Объем накопителя SSD','Не указано')
                elif drive_type == 'HDD':
                    storage_volume = res_dict.get('Объем накопителя HDD','Не указано')
                print(os,cpu,frequency,cores,diagonal,screen_resolution,ram,drive_type,storage_volume,sep='\n')
                
                # * чищу переменную, чтобы в следующей итерации он был пустым
                res_dict = dict()
                # * этот метод потому что есть возможность что этот продукт уже есть в базе
                notebook, _ = Notebook.objects.get_or_create({name:title,
                                        price:price,
                                        os:os,
                                        CPU:cpu,
                                        frequency:frequency,
                                        cores:cores,
                                        diagonal:diagonal,
                                        screen_resolution:screen_resolution,
                                        RAM:ram,
                                        hard_disk_type:drive_type,
                                        storage_volume:storage_volume
                })
                
                # * записываю айдишку
                id_list.append(notebook.id)
        # * запускаю провурку после того как прошелся по всем страницам
        self.check(id_list)
            
    # * метод который будет удалять все продукты которые удаляются из базы
    def check(self,list_id):
        # * вытаскиваем все обьекты из базы
        obj_list = Notebook.objects.all()
        # * проходимся по каждому обьекту
        for obj in obj_list:
            # * если айди обьекта нет в списке пройденных айди, то очищаем из базы 
            if obj.id not in list_id:
                obj.delete()
        print('Проверка пройдена')
        
    # * этот метод нужен чтобы запустить парсер одной командой
    def up(self,category):
        full_pages = self.get_full_pages(category)
        self.parse(full_pages)

a = ParserKivano()
a.up('noutbuki')

    
    
    
# * selery выучить потом
# @task
# def asd():
#     a = ParserServiceKivano()
#     a.up()



# multiuploatimage

# * налог курс сравнение стран мишины 