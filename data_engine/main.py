import sys
from reader import read_file
from profiler import profile_data
from cleaner import clean_data
from analyser import analyse_data
from reporter import save_report

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
        return

    input_file = sys.argv[1]

    df = read_file(input_file)

    print("Original data profile:")
    original_report = profile_data(df)
    print(original_report)

    cleaned_df = clean_data(df)

    print("\nCleaned data profile:")
    cleaned_report = profile_data(cleaned_df)
    print(cleaned_report)

    analysis_report = analyse_data(cleaned_df)

    print("\nAnalysis Report:")
    print(analysis_report)

    final_report = {
    "original_profile": original_report,
    "cleaned_profile": cleaned_report,
    "analysis": analysis_report
}

    save_report(final_report, "../storage/outputs/report.json")
    print("\nReport saved as: report.json")

    output_file = "../storage/outputs/cleaned_" + input_file.split("/")[-1]
    cleaned_df.to_csv(output_file, index=False)

    print(f"\nCleaned file saved as: {output_file}")


if __name__ == "__main__":
    main()