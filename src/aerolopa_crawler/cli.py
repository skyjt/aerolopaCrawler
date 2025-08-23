"""AeroLOPA 爬虫命令行接口"""

import argparse
import logging
import sys
from typing import List

from .config import load_config
from .aerolopa_crawler import AerolopaCrawler
from .airlines import get_supported_iata_codes


def setup_logging(verbose: bool = False) -> None:
    """配置日志输出"""

    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def list_supported_airlines() -> None:
    """列出所有支持的航空公司"""
    from .airlines import get_all_airlines

    airlines = get_all_airlines()
    print("\n支持的航空公司：")
    print("-" * 50)

    for iata, (chinese_name, english_name) in sorted(airlines.items()):
        print(f"{iata:3} | {chinese_name:20} | {english_name}")

    print(f"\n共支持 {len(airlines)} 家航空公司")


def validate_airline_codes(airline_codes: List[str]) -> List[str]:
    """验证航空公司 IATA 代码"""

    supported_codes = set(get_supported_iata_codes())
    valid_codes: List[str] = []
    invalid_codes: List[str] = []

    for code in airline_codes:
        code = code.upper().strip()
        if code in supported_codes:
            valid_codes.append(code)
        else:
            invalid_codes.append(code)

    if invalid_codes:
        print(
            f"警告：不支持的航空公司代码：{', '.join(invalid_codes)}",
            file=sys.stderr,
        )
        print("使用 --list-airlines 查看支持的航空公司", file=sys.stderr)

    return valid_codes


def parse_airline_codes(codes_input: str) -> List[str]:
    """解析命令行输入的航空公司代码"""

    if not codes_input:
        return []

    codes = [code.strip().upper() for code in codes_input.split(",")]
    return [code for code in codes if code]


def main() -> None:
    """CLI 主入口"""

    parser = argparse.ArgumentParser(
        description="AeroLOPA 座位图爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s --airline CA                    # 抓取国航座位图
  %(prog)s --airline "CA,MU,CZ"            # 抓取多家航空公司
  %(prog)s --all-airlines                  # 抓取所有支持的航空公司
  %(prog)s --list-airlines                 # 列出支持的航空公司
  %(prog)s --airline CA --verbose          # 开启详细日志
        """,
    )

    # 主操作参数（互斥）
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        "--airline",
        "-a",
        help="逗号分隔的航空公司 IATA 代码列表，例如 'CA,MU,CZ'",
    )

    action_group.add_argument(
        "--all-airlines",
        action="store_true",
        help="抓取所有支持的航空公司座位图",
    )

    action_group.add_argument(
        "--list-airlines",
        action="store_true",
        help="列出所有支持的航空公司并退出",
    )

    # 可选参数
    parser.add_argument("--verbose", "-v", action="store_true", help="输出详细日志")

    parser.add_argument("--output-dir", help="结果输出目录（覆盖配置文件）")

    parser.add_argument("--stats", action="store_true", help="任务完成后显示统计信息")

    args = parser.parse_args()

    # 配置日志
    setup_logging(args.verbose)

    try:
        # 如果仅列出航空公司
        if args.list_airlines:
            list_supported_airlines()
            return

        # 加载配置
        config = load_config()

        # 如指定输出目录则覆盖配置
        if args.output_dir:
            config.crawler.output_dir = args.output_dir

        # 初始化爬虫
        crawler = AerolopaCrawler(config)

        # 决定抓取哪些航空公司
        if args.all_airlines:
            print("开始抓取所有支持的航空公司...")
            total_processed = crawler.crawl_all_airlines()

        elif args.airline:
            airline_codes = parse_airline_codes(args.airline)
            valid_codes = validate_airline_codes(airline_codes)

            if not valid_codes:
                print("错误：未提供有效的航空公司代码", file=sys.stderr)
                sys.exit(1)

            print(f"开始抓取航空公司：{', '.join(valid_codes)}")

            total_processed = 0
            for airline_code in valid_codes:
                processed = crawler.crawl_airline_seatmaps(airline_code)
                total_processed += processed

        # 显示结果
        print("\n抓取任务完成")
        print(f"处理的座位图总数: {total_processed}")
        print(f"结果保存于: {config.crawler.output_dir}")

        # 如需显示统计信息
        if args.stats:
            stats = crawler.get_crawl_statistics()
            print("\n抓取统计：")
            print("-" * 30)
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")

    except KeyboardInterrupt:
        print("\n用户中断", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error(f"抓取失败: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
