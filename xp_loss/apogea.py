import csv

total_xp = 0
with open('xp_loss_exponential.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['lvl', 'xp', 'total_xp','die_loss', 'pct_current_lvl_loss'])
    for lvl in range(1, 31):
        xp = 50 * lvl ** 2 * (1 + lvl / 2)
        total_xp += xp
        die_loss = 0.1 * total_xp
        pct_current_lvl_loss = (die_loss / xp) * 100
        writer.writerow([lvl, int(xp), int(total_xp), int(die_loss), f'{pct_current_lvl_loss:.2f}%'])