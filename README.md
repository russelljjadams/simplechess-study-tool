# Chess Study Tool 

A Python-based toolkit designed to simplify training. It fetches your chess games from [chess.com](https://www.chess.com), executes an analysis via Stockfish, and compiles critical positions for study.

## Features

- Retrieval of games from the previous month automatically via the chess.com APIs.
- In-depth game analysis utilizing the Stockfish engine. (Ignores bullet and blitz games. This can be changed.)
- Curated list of critical positions compiled into a PGN file for study.

## Prerequisites

- Python 3.6 or higher. (Other versions will probably work, too.)
- Stockfish chess engine installed on your device.

## Installation

Begin by cloning the repository to your system:

```bash
git clone https://github.com/russelljjadams/simplechess/simplechess-study-tool.git
cd chess-study-tool
```

## Configuration

Create your personalized configuration through a JSON file, allowing for easy updates and management. On the initial run, the tool prompts you for:

- Your chess.com username.
- The location of your installed Stockfish engine.
- Your preferred analysis depth.

This information will be stored in a specified JSON configuration file.

## Usage

Start the application:

```bash
python main.py
```

Enter the name of your configuration file when prompted (minus the `.json` extension). If it doesn't exist, the tool will generate a new one. The tool then fetches your games, conducts an analysis, and extracts study positions.

The positions are available in a PGN file for review at `to_study/moves_to_study_{username}.pgn`.

## Workflow Recommendation

1. At the beginning of a new month, run the tool to process the preceding month's games.
2. Study the resulting positions throughout the month.
3. A streamlined approach: upload the PGN file to [Chessable](https://www.chessable.com) to take advantage of their spaced repetition features. For non-premium users, be mindful of the 100 positions limit per PGN upload. If needed, use the split_pgn function provided below to break your PGN into appropriately sized files.

4. Repeat monthly.

## Splitting PGN files for Non-Premium Chessable Accounts

For users without a Chessable premium account, the `split_pgn` function is used to partition your PGN into multiple files with a maximum of 100 positions each. This allows you to upload all of your positions to Chessable across multiple files.

## Contributions

Your suggestions, bug reports, and contributions enhance the project. Please create an issue or submit a pull request on GitHub.

## License

Distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.