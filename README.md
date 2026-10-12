## Симуляция работы всех уровней модели OSI.

### L7 - Прикладной (l7_http.py)

- [x] Сформировать HTTP-запрос: GET / HTTP/1.1 + Host + User-Agent<br>
- [x] Сформировать HTTP-ответ с кодом, заголовками, body<br>
- [x] Распарсить запрос/ответ обратно из байтов в структуру<br>
- [x] Поддержать DNS-запрос: example.com -> 93.184.216.34 (хотя бы заглушкой)<br>
- [x] *DONE*

### L6 - Представления (l6_presentation.py)

Кодировка текста: str <-> utf-8 bytes<br>
- [x] Шифрование/дешифровка заглушка<br>
- [ ] Сжатие/разжатие (gzip)<br>
- [ ] Сериализация JSON<br>
- [ ] *DONE*

### L5 - Сеансовый (l5_session.py)

- [x] Установить сессию: session_id, client/server, состояние ESTABLISHED/CLOSED<br>
- [ ] Привязка нескольких запросов к одной сессии (cookies/token)<br>
- [x] Корректное закрытие сессии<br>
- [ ] *DONE*

### L4 - Транспортный (l4_tcp.py)

- [x] TCP-сегмент: src_port, dst_port, seq, ack, flags (SYN/ACK/FIN/PSH), window, checksum<br>
- [x] 3-way handshake: SYN -> SYN-ACK -> ACK лог<br>
- [x] Разбивка на сегменты и сборка по seq<br>
- [ ] UDP-вариант: только порты + длина, без handshake<br>
- [ ] *DONE*

### L3 - Сетевой (l3_ip.py)

- [ ] IP-пакет: src_ip, dst_ip, TTL, protocol (6=TCP/17=UDP), checksum, payload<br>
- [ ] Уменьшение TTL на каждом "роутере", отброс при TTL=0<br>
- [ ] Таблица маршрутизации: 192.168.1.0/24 -> eth0, 0.0.0.0/0 -> gateway<br>
- [ ] Фрагментация по MTU (1500) и сборка<br>
- [ ] *DONE*

### L2 - Канальный (l2_ethernet.py)

- [ ] Ethernet-кадр: src_mac, dst_mac, ethertype (0x0800=IP, 0x0806=ARP), FCS<br>
- [ ] ARP-таблица: IP -> MAC, запрос who has 192.168.1.1?<br>
- [ ] Проверка FCS / отброс битого кадра<br>
- [ ] *DONE*

### L1 - Физический (l1_physical.py)

- [ ] Превращение кадра в bits / hex-dump как в Wireshark<br>
- [ ] Симуляция задержки, потери, повреждения бита<br>
- [ ] Подсчёт скорости/времени передачи<br>
- [ ] Проверка: hex-dump твоего кадра разбирается глазами<br>
- [ ] *DONE*
