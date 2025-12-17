# SYSTEM CONTEXT RESTORE PROTOCOL v5.2 (ULTIMATE)
# Updated: 2025-12-05
# Status: LIVE

## 1. NHẬN DIỆN NGƯỜI DÙNG (IDENTITY)
- **User:** Thang (Sinh viên Năm 2 - Kỹ thuật Điện/EE - ĐH Bách Khoa TP.HCM - HCMUT).
- **Style:** Hardcore Engineering. Ưu tiên CLI. Ghét Bloatware. "Stability First".
- **Nhiệm vụ chính:** Code C/C++ (VS Code), Altium Designer (PCB 3D), FPGA (Vivado), AI/Data.
- **Data**: C cài Windows, D lưu dữ liệu, E backup; CLI đang ở trong WSL của D.

## 2. CẤU HÌNH PHẦN CỨNG (HP ELITEBOOK 845 G8)
- **CPU:** AMD Ryzen 5 PRO 5650U (6 nhân / 12 luồng).
    - *Tweak:* Power Plan 99% (Tắt Turbo Boost khi không cần thiết để mát máy).
- **RAM:** 32GB DDR4 3200MHz (Advantech Industrial - Part: SQR-SD4N16G3K2SNCB).
    - *Specs:* Chip Samsung/Micron A-die. Mạ vàng 30µ". Industrial Grade (-20°C đến 85°C).
    - *Validation:* Passed TM5 Extreme1@anta777 (1h15m) & OCCT AVX2. Rock Stable.
- **Wifi/Bluetooth:** Qualcomm FastConnect 6900 Wi-Fi 6E.
    - *Feature:* Dual Band Simultaneous (DBS) - Kết nối 2 băng tần cùng lúc. Bluetooth 5.2.
- **Storage:** SSD NVMe 512GB (Original).
    - *Health:* Good (100%). Available Spare: 100%.
    - *Stats:* Power On Hours: ~33k (High). Writes: ~19TB (Low - Rất tốt).
    - *History:* Máy từng chạy Server/Kiosk (Bật nhiều, Ghi ít).

## 3. CẤU HÌNH MÔI TRƯỜNG (ENV CONFIG)
- **WSL 2 Config (.wslconfig) - Optimized for 32GB RAM:**
    ```ini
    [wsl2]
    memory=16GB
    processors=8
    swap=8GB
    swapFile=D:\\WSL_Swap\\swap.vhdx
    [experimental]
    autoMemoryReclaim=gradual
    ```
- **System Tuning:**
    - **TCP Congestion:** BBR (Enabled).
    - **Windows Defender:** Exclusion added for WSL virtual disk (`ext4.vhdx`) & `vmwp.exe`.
    - **Memory Allocator:** `Mimalloc` (LD_PRELOAD).

## 4. KHO CÔNG CỤ (TOOLKIT)
- **Engineering Core (Linux/WSL):**
    - `build-essential`, `g++`, `cmake`, `gdb`: C/C++ Stack.
    - `iverilog`, `gtkwave`: FPGA/Verilog Simulation.
    - `stress-ng`: Stress test hệ thống.
- **System Utilities:**
    - `htop`, `btop`: Monitor.
    - `ncdu`: Disk usage.
    - `zoxide`: Smart navigation.
- **Local Scripts (`misc/`):**
    - `init_zram.sh`: Bật ZRAM (Cần sudo).
    - `ram_verify/`: Các tool check RAM native C.

## 5. QUY TRÌNH BẢO TRÌ (MAINTENANCE PROTOCOL)
- **Vệ sinh Màn hình:**
    - *Dụng cụ:* Khăn lau kính mắt (Microfiber) + Hơi thở (Hà hơi).
    - *Tuyệt đối:* KHÔNG dùng cồn hay khăn ướt (Uniku) lên màn hình.
- **Vệ sinh Vỏ/Phím:**
    - *Dụng cụ:* Khăn ướt Uniku **VẮT THẬT KHÔ**. Lau xong lau lại bằng khăn khô ngay.
- **RAM Upgrade:**
    - *Rule:* Chỉ mua RAM Industrial hoặc Samsung/Hynix chuẩn JEDEC. Say NO to Gaming RAM.

## 6. QUY TẮC AI
- Bỏ qua thủ tục hỏi cấu hình.
- Tập trung vào Code (C++/Python) và Engineering.

## Gemini Added Memories
- Project 'wifi_bot' set up successfully using Selenium/Python + tmux for auto-login KTX wifi. User credentials default to awing15-15.
- KTX Wifi portal behavior: Has a survey page (skippable via 'Remind me later' or filling fake info), followed by a hidden login form (id='frmLogin') that needs forced submission via JS. Auto-login bot is updated to handle this.
- User is satisfied with the optimized Wifi Bot (Selenium + Active Refresh) and considers it powerful.
- University schedule timing: Period 1 starts at 06:00 AM, and each period lasts exactly 1 hour.
