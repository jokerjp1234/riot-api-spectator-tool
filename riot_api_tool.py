            tool.add_player_to_monitor(game_name, tag_line, region, cluster)
            except (ValueError, IndexError):
                print("無効な選択です")

        elif choice == "2":
            game_name = input("削除するゲーム名を入力: ").strip()
            tag_line = input("削除するタグラインを入力: ").strip()
            tool.remove_player_from_monitor(game_name, tag_line)

        elif choice == "3":
            tool.list_monitored_players()

        elif choice == "4":
            print("\n利用可能地域:")
            available_regions = list(tool.pro_players.keys())
            for i, region in enumerate(available_regions):
                print(f"{i+1}. {region}")

            try:
                region_idx = int(input(f"地域を選択 (1-{len(available_regions)}): ")) - 1
                region = available_regions[region_idx]
                tool.add_pro_players_by_region(region)
            except (ValueError, IndexError):
                print("無効な選択です")

        elif choice == "5":
            tool.start_monitoring()
            print("\n監視を開始しました。Ctrl+C で停止できます。")
            try:
                while tool.monitoring:
                    time.sleep(1)
            except KeyboardInterrupt:
                tool.stop_monitoring()

        elif choice == "6":
            tool.stop_monitoring()

        elif choice == "7":
            print("\n=== 利用可能地域 ===")
            for region, url in tool.regional_urls.items():
                cluster = tool.region_to_cluster.get(region, "不明")
                print(f"{region}: {cluster} クラスター")

        elif choice == "8":
            analytics = tool.get_analytics_data()
            if 'error' in analytics:
                print(f"エラー: {analytics['error']}")
            else:
                print("\n=== 分析データ ===")
                print(f"総ゲーム数: {analytics['basic_stats']['total_games']}")
                print(f"平均ゲーム時間: {analytics['basic_stats']['avg_duration']} 秒")
                print(f"監視プレイヤー数: {analytics['basic_stats']['unique_players']}")
                
                if analytics['player_stats']:
                    print("\n=== プレイヤー統計 ===")
                    for stat in analytics['player_stats']:
                        print(f"{stat['game_name']}#{stat['tag_line']}: {stat['games_played']} ゲーム")

if __name__ == "__main__":
    main()
