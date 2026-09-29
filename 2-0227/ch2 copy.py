import math
import matplotlib.pyplot as plt

# 解決中文顯示與負號問題
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def calculate_angles(distance):
    """根據目標水平距離計算砲彈的兩種仰角（低仰角與高仰角）"""
    V_kmh = 100          # 初速 km/hr
    V = V_kmh / 3.6     # 換算成 m/s
    g = 9.81            # 重力加速度 m/s^2

    # sin(2θ) = Rg / V²
    value = distance * g / (V ** 2)

    # 超過最大理論射程
    if value > 1:
        return None

    angle1 = math.degrees(0.5 * math.asin(value))
    angle2 = 90.0 - angle1

    return angle1, angle2

def plot_military_ballistics(distance, angle1, angle2):
    """繪製符合正規軍事外彈道規範的彈道軌跡圖"""
    V = 100 / 3.6
    g = 9.81

    # 密位換算：軍規標準 1度 = 6400 / 360 ≈ 17.7778 mils
    mil1 = angle1 * (6400 / 360)
    mil2 = angle2 * (6400 / 360)

    # 物理量計算：最大彈道高 (Max Ordinate, H_max) 與 飛行時間 (Time of Flight, Tf)
    rad1, rad2 = math.radians(angle1), math.radians(angle2)
    h_max1 = ((V * math.sin(rad1)) ** 2) / (2 * g)
    h_max2 = ((V * math.sin(rad2)) ** 2) / (2 * g)
    tf1 = (2 * V * math.sin(rad1)) / g
    tf2 = (2 * V * math.sin(rad2)) / g

    # 生成平滑軌跡點
    def get_trajectory_coords(angle, tf):
        rad = math.radians(angle)
        vx = V * math.cos(rad)
        vy = V * math.sin(rad)
        pts = 400
        x_coords, y_coords = [], []
        for i in range(pts + 1):
            t = (tf * i) / pts
            x = vx * t
            y = vy * t - 0.5 * g * (t ** 2)
            x_coords.append(x)
            y_coords.append(max(0.0, y))
        return x_coords, y_coords

    x1, y1 = get_trajectory_coords(angle1, tf1)
    x2, y2 = get_trajectory_coords(angle2, tf2)

    # 建立畫布（不使用 default 樣式重置字型）
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=100)

    # 1. 繪製彈道軌跡線
    ax.plot(x1, y1, color='#0044cc', linewidth=2.2, label=f'低仰角射擊 (Low-Angle Fire) - {angle1:.1f}° [{mil1:.0f} mils]')
    ax.plot(x2, y2, color='#cc2200', linewidth=2.2, linestyle='--', label=f'高仰角曲射 (High-Angle Fire) - {angle2:.1f}° [{mil2:.0f} mils]')

    # 2. 標記頂點 (Max Ordinate / Vertex) - 改用標準數字 1 與 2
    apex_x = distance / 2
    ax.scatter([apex_x], [h_max1], color='#0044cc', s=45, zorder=5)
    ax.vlines(apex_x, 0, h_max1, color='#0044cc', linestyle=':', alpha=0.6)
    ax.annotate(f'Hmax1: {h_max1:.2f} m', xy=(apex_x, h_max1), xytext=(apex_x + 1.2, h_max1 + 0.3),
                fontsize=9, color='#0044cc', fontweight='bold')

    ax.scatter([apex_x], [h_max2], color='#cc2200', s=45, zorder=5)
    ax.vlines(apex_x, 0, h_max2, color='#cc2200', linestyle=':', alpha=0.6)
    ax.annotate(f'Hmax2: {h_max2:.2f} m', xy=(apex_x, h_max2), xytext=(apex_x + 1.2, h_max2 + 0.5),
                fontsize=9, color='#cc2200', fontweight='bold')

    # 3. 標記發射陣地與目標點
    ax.scatter([0], [0], color='black', s=100, marker='^', zorder=6, label='發射陣地 (Gun Position)')
    ax.scatter([distance], [0], color='red', s=120, marker='X', zorder=6, label='目標彈著點 (Target/Impact)')
    
    ax.axhline(0, color='#333333', linewidth=1.5)

    # 4. 建立軍事射擊諸元數據欄 - 改用標準數字 1 與 2
    info_text = (
        "【射擊諸元分析表 (Firing Solutions)】\n"
        f"• 目標距離 (Target Range) : {distance:.2f} m\n"
        f"• 砲口初速 (Muzzle Velocity): {V:.2f} m/s ({V*3.6:.0f} km/h)\n"
        "------------------------------------\n"
        f"• 低仰角 (θ1) : {angle1:.2f}° ({mil1:.0f} mils)\n"
        f"  - 彈道頂點高 (Hmax1): {h_max1:.2f} m\n"
        f"  - 飛行時間 (ToF1)   : {tf1:.2f} s\n"
        f"  - 落角 (Angle of Fall): {angle1:.2f}°\n"
        "------------------------------------\n"
        f"• 高仰角 (θ2) : {angle2:.2f}° ({mil2:.0f} mils)\n"
        f"  - 彈道頂點高 (Hmax2): {h_max2:.2f} m\n"
        f"  - 飛行時間 (ToF2)   : {tf2:.2f} s\n"
        f"  - 落角 (Angle of Fall): {angle2:.2f}°"
    )
    ax.text(0.97, 0.95, info_text, transform=ax.transAxes, fontsize=9.5,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='square,pad=0.8', facecolor='#f8f9fa', edgecolor='#555555', alpha=0.92))

    # 圖表坐標軸與軍規網格設定
    ax.set_title("砲兵外彈道分析圖 (Exterior Ballistic Trajectory Chart)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("水平射程 Range X (m)", fontsize=11, fontweight='bold')
    ax.set_ylabel("彈道高 Altitude Y (m)", fontsize=11, fontweight='bold')
    
    ax.set_ylim(-1.0, max(h_max2 * 1.2, 5.0))
    ax.set_xlim(-distance * 0.05, distance * 1.15)
    
    # 雙向細格線
    ax.minorticks_on()
    ax.grid(which='major', linestyle='-', linewidth=0.7, color='#b0b0b0')
    ax.grid(which='minor', linestyle=':', linewidth=0.5, color='#d8d8d8')
    
    ax.legend(loc='upper left', framealpha=0.9)
    plt.tight_layout()
    plt.show()

def main():
    print("=== 砲兵外彈道射擊諸元計算與彈道圖 ===")
    V_kmh = 100
    m = 100
    g = 9.81
    V = V_kmh / 3.6
    max_range = (V ** 2) / g

    print(f"初速：{V_kmh} km/hr ({V:.2f} m/s)")
    print(f"彈重：{m} kg")
    print(f"重力加速度：{g} m/s²")
    print(f"最大理論射程：{max_range:.2f} m\n")

    try:
        distance = float(input("請輸入目標水平距離（公尺）："))
    except ValueError:
        print("輸入格式錯誤，請輸入數值。")
        return

    result = calculate_angles(distance)
    if result is None:
        print(f"\n[警示] 目標距離 {distance:.2f} m 超過最大理論射程 ({max_range:.2f} m)，無法解算射角。")
        return

    angle1, angle2 = result
    print(f"\n解算完成：低仰角 = {angle1:.2f}°，高仰角 = {angle2:.2f}°")
    print("正在繪製軍規外彈道圖表...")
    plot_military_ballistics(distance, angle1, angle2)

if __name__ == '__main__':
    main()