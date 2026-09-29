import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.ticker as ticker

# 解決繁體中文顯示與負號破圖問題
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang TC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def calculate_trajectory_data(distance, v_kmh):
    """計算射角與相關外彈道物理量"""
    g = 9.81
    V = v_kmh / 3.6
    max_range = (V ** 2) / g
    value = distance * g / (V ** 2)

    # 超出理論最大射程
    if value > 1.0:
        return None

    # 解算仰角（度數與密位）
    angle1 = math.degrees(0.5 * math.asin(value))
    angle2 = 90.0 - angle1
    mil1 = angle1 * (6400 / 360)
    mil2 = angle2 * (6400 / 360)

    # 頂點高與飛行時間
    rad1, rad2 = math.radians(angle1), math.radians(angle2)
    h_max1 = ((V * math.sin(rad1)) ** 2) / (2 * g)
    h_max2 = ((V * math.sin(rad2)) ** 2) / (2 * g)
    tf1 = (2 * V * math.sin(rad1)) / g
    tf2 = (2 * V * math.sin(rad2)) / g

    # 產生平滑軌跡點
    def gen_points(angle, tf):
        rad = math.radians(angle)
        vx = V * math.cos(rad)
        vy = V * math.sin(rad)
        pts = 400
        x_pts, y_pts = [], []
        for i in range(pts + 1):
            t = (tf * i) / pts
            x = vx * t
            y = vy * t - 0.5 * g * (t ** 2)
            x_pts.append(x)
            y_pts.append(max(0.0, y))
        return x_pts, y_pts

    x1, y1 = gen_points(angle1, tf1)
    x2, y2 = gen_points(angle2, tf2)

    return {
        'V': V,
        'max_range': max_range,
        'angle1': angle1, 'mil1': mil1, 'h_max1': h_max1, 'tf1': tf1, 'x1': x1, 'y1': y1,
        'angle2': angle2, 'mil2': mil2, 'h_max2': h_max2, 'tf2': tf2, 'x2': x2, 'y2': y2
    }

def main():
    # 符合真實火砲情境的初始數值：目標 8 公里 (8000 m)、初速約 450 m/s (1620 km/h)
    init_dist = 8000.0   
    init_vel = 1620.0   

    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=100)
    plt.subplots_adjust(bottom=0.22, top=0.92)

    # 基本坐標軸與軍規網格配置
    ax.axhline(0, color='#333333', linewidth=1.5)
    ax.minorticks_on()
    ax.grid(which='major', linestyle='-', linewidth=0.7, color='#b0b0b0')
    ax.grid(which='minor', linestyle=':', linewidth=0.5, color='#e5e5e5')
    
    # 數值大時使用千分位顯示 (例如 10,000 m)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'{int(y):,}'))

    ax.set_title("火砲外彈道即時模擬解算系統", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("水平射程 Range X (公尺 / m)", fontsize=11, fontweight='bold')
    ax.set_ylabel("彈道高 Altitude Y (公尺 / m)", fontsize=11, fontweight='bold')

    # 初始化繪圖圖元
    line1, = ax.plot([], [], color='#0044cc', linewidth=2.2)
    line2, = ax.plot([], [], color='#cc2200', linewidth=2.2, linestyle='--')
    apex1_scat = ax.scatter([], [], color='#0044cc', s=50, zorder=5)
    apex2_scat = ax.scatter([], [], color='#cc2200', s=50, zorder=5)
    gun_scat = ax.scatter([0], [0], color='black', s=100, marker='^', zorder=6, label='發射陣地 (Gun Position)')
    target_scat = ax.scatter([], [], color='red', s=120, marker='X', zorder=6, label='目標彈著點 (Target/Impact)')

    apex1_text = ax.text(0, 0, '', fontsize=9, color='#0044cc', fontweight='bold')
    apex2_text = ax.text(0, 0, '', fontsize=9, color='#cc2200', fontweight='bold')
    warning_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, color='crimson',
                           fontsize=16, fontweight='bold', ha='center', va='center')

    info_box = ax.text(0.97, 0.95, '', transform=ax.transAxes, fontsize=9.5,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='square,pad=0.8', facecolor='#f8f9fa', edgecolor='#555555', alpha=0.92))

    def update(val=None):
        dist = s_dist.val
        vel = s_vel.val
        data = calculate_trajectory_data(dist, vel)

        if data is None:
            # 超程警示
            line1.set_data([], [])
            line2.set_data([], [])
            apex1_scat.set_offsets([[-99999, -99999]])
            apex2_scat.set_offsets([[-99999, -99999]])
            target_scat.set_offsets([[dist, 0]])
            apex1_text.set_text('')
            apex2_text.set_text('')
            
            v_curr = vel / 3.6
            max_r = (v_curr ** 2) / 9.81
            warning_text.set_text(f"【警示】目標距離 ({dist:,.0f} m) 超出當前初速最大射程 ({max_r:,.0f} m)！")
            
            info_box.set_text(
                "【射擊諸元無效】\n"
                f"• 目標距離 : {dist:,.0f} m ({dist/1000:.1f} km)\n"
                f"• 砲口初速 : {v_curr:.1f} m/s ({vel:.0f} km/h)\n"
                f"• 理論最大射程 : {max_r:,.0f} m ({max_r/1000:.1f} km)\n"
                "------------------------------------\n"
                "狀態：超出最大射程 (Out of Range)"
            )
            ax.set_xlim(-dist * 0.05, dist * 1.15)
            ax.set_ylim(-dist * 0.02, dist * 0.4)
        else:
            warning_text.set_text('')
            line1.set_data(data['x1'], data['y1'])
            line1.set_label(f"低仰角射擊 - {data['angle1']:.1f}° [{data['mil1']:.0f} mils]")
            line2.set_data(data['x2'], data['y2'])
            line2.set_label(f"高仰角曲射 - {data['angle2']:.1f}° [{data['mil2']:.0f} mils]")

            apex_x = dist / 2
            apex1_scat.set_offsets([[apex_x, data['h_max1']]])
            apex2_scat.set_offsets([[apex_x, data['h_max2']]])
            target_scat.set_offsets([[dist, 0]])

            apex1_text.set_position((apex_x + dist * 0.015, data['h_max1'] + data['h_max2'] * 0.015))
            apex1_text.set_text(f"Hmax1: {data['h_max1']:,.1f} m")

            apex2_text.set_position((apex_x + dist * 0.015, data['h_max2'] + data['h_max2'] * 0.015))
            apex2_text.set_text(f"Hmax2: {data['h_max2']:,.1f} m")

            info_box.set_text(
                "【射擊諸元分析表 (Firing Solutions)】\n"
                f"• 目標距離 (Target Range) : {dist:,.0f} m ({dist/1000:.2f} km)\n"
                f"• 砲口初速 (Muzzle Velocity): {data['V']:.1f} m/s ({vel:.0f} km/h)\n"
                f"• 理論最大射程 (Max Range) : {data['max_range']:,.0f} m ({data['max_range']/1000:.1f} km)\n"
                "------------------------------------\n"
                f"• 低仰角 (θ1) : {data['angle1']:.2f}° ({data['mil1']:.0f} mils)\n"
                f"  - 彈道頂點高 (Hmax1): {data['h_max1']:,.1f} m\n"
                f"  - 飛行時間 (ToF1)   : {data['tf1']:.2f} 秒\n"
                f"  - 落角 (Angle of Fall): {data['angle1']:.2f}°\n"
                "------------------------------------\n"
                f"• 高仰角 (θ2) : {data['angle2']:.2f}° ({data['mil2']:.0f} mils)\n"
                f"  - 彈道頂點高 (Hmax2): {data['h_max2']:,.1f} m\n"
                f"  - 飛行時間 (ToF2)   : {data['tf2']:.2f} 秒\n"
                f"  - 落角 (Angle of Fall): {data['angle2']:.2f}°"
            )

            # 動態視角調整
            ax.set_xlim(-dist * 0.05, dist * 1.15)
            ax.set_ylim(-max(data['h_max2'] * 0.03, 10.0), max(data['h_max2'] * 1.25, 100.0))
            ax.legend(loc='upper left', framealpha=0.9)

        fig.canvas.draw_idle()

    # 建立符合常規真實尺度的滑桿控制軸
    ax_dist = plt.axes([0.15, 0.08, 0.7, 0.03], facecolor='#e9ecef')
    ax_vel = plt.axes([0.15, 0.03, 0.7, 0.03], facecolor='#e9ecef')

    # 目標距離：500 m ~ 30,000 m (30 公里)，步進 100 公尺
    s_dist = Slider(ax_dist, '目標距離 (m)', 100.0, 30000.0, valinit=init_dist, valstep=100.0, color='#4a90e2')
    # 砲口初速：360 km/h (100 m/s) ~ 3600 km/h (1000 m/s)，步進 20 km/h
    s_vel = Slider(ax_vel, '初速 (km/h)', 360.0, 3600.0, valinit=init_vel, valstep=20.0, color='#e67e22')

    s_dist.on_changed(update)
    s_vel.on_changed(update)

    update()
    plt.show()

if __name__ == '__main__':
    main()