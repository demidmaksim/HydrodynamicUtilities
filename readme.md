# HydrodynamicModelAnalysis

HydrodynamicModelAnalysis – HydrodynamicModelAnalysis is an up-and-coming library for the reservoir engineer doing hydrodynamic modeling in [tNavigator](https://rfdyn.com/) or [Eclipse](https://software.slb.ru/products/eclipse/).

This repository is a set of tools for quickly creating a model schedule section, calculating production history for wells based on measurements, converting well trajectories between different formats, reading eclipse binary files, parsing .data files of models and uploading calculation results

Additionally, the repository has the ability to build an application that fellow hydrodynamicists can use to schedule without any knowledge of python

The main sections of the repository are:
- **App** - Files for building the application
- **Example** - Code usage examples
- **Models** - This package provides various tools for working with data
    - **DataFile** - .data file objects
      - **Sections** - Sections and keywords of .data files
    - **EclipseBinaryFile** - Tools for working with eclipse binary files 
    - **ExcelFile** - Tools for working with excel spreadsheets
    - **HistoryData** - Tools for working with the history of wells
    - **ParamVector** - Tools for working with time series
    - **Strategy** - Tools for working with model schedules
    - **Time** - Tools for working with time, all modules of this repository use time series from this package. It is based on [np.datetime64](https://numpy.org/doc/stable/reference/arrays.datetime.html).
    - **Well** - Tools for working with well trajectories
- **Reader** - Tools for reading various files
    - **EclipseBinaryParser** - Parser for eclipse binary files
    - **ExcelReader** - Tools for reading excel files
    - **ReaderAscii** -  Parser for [tNavigator](https://rfdyn.com/) or [Eclipse](https://software.slb.ru/products/eclipse/) .data files
    - **WellFile** - Tools for reading files with toolpaths
- **Writer** - Tools for writing to files
  - Schedule - Tools for writing to files in the schedule section 


# HydrodynamicModelAnalysis

HydrodynamicModelAnalysis – это развивающаяся в меру сил библиотека для инженера-нефтяника, занимающегося гидродинамическим моделированием в [tNavigator](https://rfdyn.com/) или [Eclipse](https://software.slb.ru/products/eclipse/).

Этот репозиторий является набором инструментов для быстрого создания секции расписания моделей, расчет истории добычи по скважинам на основе замеров, конвертация траекторий скважин между различными форматами, чтение бинарных файлов формата eclipse, анализ .data файлов моделей и выгрузка результатов расчетов 

Дополнительно в репозитории есть возможность собрать приложение, которое могут использовать коллеги-гидродинамики для составления расписания без каких-либо знаний python

Основными разделами репозитория являются:
- **App** - файлы для сборки приложения
- **Example** - примеры использования кода
- **Models** - данный пакет предоставляет различные инструменты для работы с данными
    - **DataFile** - объекты .data файлов 
      - **Sections** - секции и ключевые слова .data файлов
    - **EclipseBinaryFile** - Инструменты для работы с бинарными файлами формата eclipse
    - **ExcelFile** - Инструменты для работы с excel таблицами
    - **HistoryData** - Инструменты для работы с историей работы скважин
    - **ParamVector** - Инструменты для работы с временными рядами
    - **Strategy** - Инструменты для работы с расписанием моделей
    - **Time** - Инструменты для работы с временем, все модули данного репозитория используют временные ряды из данного пакета. Он основан на [np.datetime64](https://numpy.org/doc/stable/reference/arrays.datetime.html).
    - **Well** - Инструменты для работы с траекториями скважин
- **Reader** - Инструменты для чтения различных файлов 
    - **EclipseBinaryParser** - Парсер бинарных файлов формата eclipse 
    - **ExcelReader** - Инструменты для чтения excel файлов 
    - **ReaderAscii** - Парсер .data файлов формата [tNavigator](https://rfdyn.com/) или [Eclipse](https://software.slb.ru/products/eclipse/)
    - **WellFile** - Инструменты для чтения файлов с траекториями
- **Writer** - Инструменты для записи в файлы 
  - Schedule - Инструменты для записи в файлы секции schedule
