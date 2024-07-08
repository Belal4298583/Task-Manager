Task Scheduling System

این پروژه یک سیستم زمانبندی وظایف را شبیه‌سازی می‌کند که شامل سه پردازنده و تعدادی وظیفه با منابع و زمانبندی‌های مشخص است. از رابط کاربری گرافیکی (GUI) برای نمایش وضعیت سیستم و استفاده از پردازنده‌ها استفاده می‌شود.

نیازمندی‌ها

برای اجرای این پروژه، نیاز به نصب کتابخانه‌های زیر دارید

   tkinter  برای رابط کاربری گرافیکی

   matplotlib  برای رسم نمودارهای استفاده از پردازنده

 برای اجرای چندنخی threading

ساختار پروژه
کد اصلی شامل بخش‌های زیر است:

   متغیرهای سراسری

   resources : یک دیکشنری که منابع موجود در سیستم را نگهداری می‌کند.

   resource_locks : قفل‌های مرتبط با هر منبع برای جلوگیری از تداخل در دسترسی همزمان.

   ready_queues : صف‌های آماده برای هر پردازنده.

   waiting_queue : صف انتظار برای وظایفی که نمی‌توانند منابع مورد نیاز را دریافت کنند.

   tasks : لیستی از وظایف با مشخصات شامل دوره، زمان اجرای اولیه، منابع مورد نیاز و تکرار.

کلاس‌ها

  MainThread یک نخ اصلی که وضعیت سیستم را به‌روزرسانی می‌کند.


 ProcessorThreadیک نخ برای هر پردازنده که وظایف را اجرا و بار را بین پردازنده‌ها متعادل می‌کند.

 GUI رابط کاربری گرافیکی که وضعیت منابع، صف‌های آماده و وظایف در حال اجرا را نمایش می‌دهد.





توابع

start_threads(gui)  نخ‌های پردازنده و نخ اصلی را راه‌اندازی می‌کند.

distribute_tasks(algorithm) وظایف را بر اساس الگوریتم زمانبندی انتخاب شده (EDF or RateMonotonic) توزیع می‌کند.

age_tasks()  وظایف در صف انتظار را مدیریت می‌کند و به صف‌های آماده منتقل می‌کند.

main() نقطه شروع برنامه که رابط کاربری گرافیکی را راه‌اندازی کرده و نخ‌های لازم را شروع می‌کند.

  اجرای برنامه

برای اجرای برنامه، کافی است دستور زیر را در ترمینال خود وارد کنید:

 Python3 osFinal.py

همچنین پروژه دارای دو نولع ورودی است یکی با تابع رند یکی به صورت دستی

ونیز کد بدون محیط گرافیکی و اولیه در دسترس است.

