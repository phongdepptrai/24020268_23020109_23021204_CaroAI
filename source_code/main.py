import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Caro AI")
    parser.add_argument(
        "--level3",
        action="store_true",
        help="Run Minimax/Alpha-Beta experiments and export result tables.",
    )
    parser.add_argument(
        "--depths",
        default="1,2,3",
        help="Comma-separated depths for --level3, for example: 1,2,3.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Folder for Level 3 CSV and Markdown reports.",
    )
    args = parser.parse_args()

    if args.level3:
        from experiments import parse_depths, run_level3_experiments

        depths = parse_depths(args.depths)
        output_dir = Path(args.output_dir) if args.output_dir else None
        results, csv_path, report_path = run_level3_experiments(
            depths=depths,
            output_dir=output_dir,
        )
        print("Level 3 experiments completed.")
        print("Rows: {0}".format(len(results)))
        print("CSV: {0}".format(csv_path))
        print("Report: {0}".format(report_path))
        return

    from game import Game

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
