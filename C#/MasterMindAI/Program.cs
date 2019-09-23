using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using IntrinsicAlgo;

namespace MasterMindAI
{
    internal static class Extensions
    {
        internal static void CopyTo(this int[,] copyFrom, int index, Span<int> copyTo)
        {
            for (int x = 0; x < copyFrom.GetLength(1); x++)
            {
                copyTo[x] = copyFrom[index, x];
            }
        }

        internal static int RemoveRows(this int[,] toShrink, bool[] rowsToRemove, int count, int columns)
        {
            int index = 0;
            for (int i = 0; i < count; i++)
            {
                if (!rowsToRemove[i])
                {
                    for (int k = 0; k < columns; k++)
                    {
                        toShrink[index, k] = toShrink[i, k];
                    }
                    index++;
                }
            }

            return index;
        }

        internal static void Foreach<T>(this T[] array, Action<T> action)
        {
            foreach (var item in array)
            {
                action(item);
            }
        }
    }

    class Program
    {
        private static int SumEquals(Span<int> a, Span<int> b)
        {
            int equals = 0;
            for (int i = 0; i < a.Length; i++)
            {
                if (a[i] == b[i])
                {
                    equals++;
                }
            }
            return equals;
        }

        private static (int blackPegs, int whitePegs) Feedback(Span<int> answer, Span<int> guess, int colorCount)
        {
            int blackPegs = GetBlackPegs(answer, guess);
            int whitePegs = GetWhitePegs(answer, guess, blackPegs, colorCount);

            return (blackPegs, whitePegs);
        }

        private static int GetBlackPegs(Span<int> answer, Span<int> guess)
        {
            return SumEquals(answer, guess);
        }

        private static int GetWhitePegs(Span<int> answer, Span<int> guess, int blackPegs, int colorCount)
        {
            Span<int> guessColors = stackalloc int[colorCount];
            Span<int> answerColors = stackalloc int[colorCount];
            for (int i = 0; i < guess.Length; i++)
            {
                guessColors[guess[i]]++;
                answerColors[answer[i]]++;
            }


            int whitePegs = 0;
            for (int color = 0; color < colorCount; color++)
            {
                int colorOccurencesInGuess = guessColors[color];
                int colorOccurencesInAnswer = answerColors[color];
                if (colorOccurencesInAnswer > 0 && colorOccurencesInGuess > 0)
                {
                    if (colorOccurencesInGuess <= colorOccurencesInAnswer)
                    {
                        whitePegs += colorOccurencesInGuess;
                    }
                    else if (colorOccurencesInGuess > colorOccurencesInAnswer)
                    {
                        whitePegs += colorOccurencesInAnswer;
                    }
                }
            }

            return whitePegs - blackPegs;
        }

        private static void PruneSearchSpace(int[,] searchSpace, int searchSpaceSize, bool[] removeRows, (int blackPegs, int whitePegs) feedback, Span<int> guess, int columns, int colorCount)
        {
            Span<int> possibleGuess = stackalloc int[columns];
            for (int z = 0; z < searchSpaceSize; z++)
            {
                searchSpace.CopyTo(z, possibleGuess);

                int blackPegs = GetBlackPegs(guess, possibleGuess);
                if (blackPegs != feedback.blackPegs)
                {
                    removeRows[z] = true;
                    continue;
                }

                int whitePegs = GetWhitePegs(guess, possibleGuess, blackPegs, colorCount);
                if (whitePegs != feedback.whitePegs)
                {
                    removeRows[z] = true;
                }
            }
        }

        private static int CreateStateSpace(int[,] stateSpace, int columnsLeft, int index, List<int> guess, int colorCount)
        {
            if (columnsLeft == 0)
            {
                for (int i = 0; i < guess.Count; i++)
                {
                    stateSpace[index, i] = guess[i];
                }
                return index + 1;
            }

            for (int i = 0; i < colorCount; i++)
            {
                guess.Add(i);
                index = CreateStateSpace(stateSpace, columnsLeft - 1, index, guess, colorCount);
                guess.RemoveAt(guess.Count - 1);
            }

            return index;
        }

        private static int BestGuess(int[,] searchSpace, bool[] removeRow, int searchSpaceSize, int columns, int colorCount, Span<int> origGuess, (int blackPegs, int whitePegs)? origFeedback)
        {
            int origFeedbackSum = 0;
            if (origFeedback.HasValue)
            {
                origFeedbackSum = origFeedback.Value.blackPegs + origFeedback.Value.whitePegs;
            }
            int bestGuessIndex = 0;
            int bestWorstCaseDecreasedSearchSpace = searchSpaceSize;
            Span<int> possibleGuess = new int[columns];
            for (int i = 0; i < searchSpaceSize; i++)
            {
                int worstCaseDecreasedSearchSpace = 0;

                //Set guess
                Span<int> guess = stackalloc int[columns];
                searchSpace.CopyTo(i, guess);

                int guessDifference = columns;
                if (origFeedback.HasValue)
                {
                    guessDifference = columns - SumEquals(guess, origGuess);
                }

                for (int blackPegs = 0; blackPegs < columns + 1; blackPegs++)
                {
                    for (int whitePegs = 0; whitePegs < columns + 1 - blackPegs; whitePegs++)
                    {
                        if (Math.Abs(origFeedbackSum - (blackPegs + whitePegs)) <= guessDifference)
                        {
                            Array.Fill(removeRow, false);

                            //Remove guess from search space
                            removeRow[i] = true;

                            var feedback = (blackPegs, whitePegs);

                            //Mark invalid states
                            PruneSearchSpace(searchSpace, searchSpaceSize, removeRow, feedback, guess, columns, colorCount);

                            int stateSize = searchSpaceSize - IntrinsicAlgos.Sum(removeRow);
                            //Console.WriteLine(stateSize);
                            if (stateSize > worstCaseDecreasedSearchSpace)
                            {
                                worstCaseDecreasedSearchSpace = stateSize;
                            }
                        }
                    }
                }
                if (worstCaseDecreasedSearchSpace < bestWorstCaseDecreasedSearchSpace)
                {
                    bestWorstCaseDecreasedSearchSpace = worstCaseDecreasedSearchSpace;
                    bestGuessIndex = i;
                }
            }
            return bestGuessIndex;
        }

        static void PlayGames(GuessType guessType, int columns, int colorCount, int gamesToPlay, LogAmount logAmount)
        {
            int stateSpaceSize = (int)Math.Pow(colorCount, columns);
            int[,] TotalSearchSpace = new int[stateSpaceSize, columns];
            int[,] searchSpace = new int[stateSpaceSize, columns];
            bool[] removeRows = new bool[stateSpaceSize];
            Random random = new Random(1223);

            CreateStateSpace(TotalSearchSpace, columns, 0, new List<int>(), colorCount);
            int totalGuessCount = 0;

            Span<int> code = new int[columns];
            Span<int> guess = new int[columns];
            Span<int> possibleGuess = new int[columns];

            Stopwatch watch = new Stopwatch();
            watch.Start();

            int maxGuesses = 0;


            int bestInitialGuess = -1;
            if (guessType == GuessType.MINMAX)
            {
                bestInitialGuess = BestGuess(TotalSearchSpace, removeRows, stateSpaceSize, columns, colorCount, guess, null);
            }

            for (int i = 0; i < gamesToPlay; i++)
            {
                Buffer.BlockCopy(TotalSearchSpace, 0, searchSpace, 0, stateSpaceSize * TotalSearchSpace.GetLength(1) * Marshal.SizeOf<int>());
                int statesCount = stateSpaceSize;

                //Set code
                searchSpace.CopyTo(random.Next(statesCount), code);

                //Set guess
                int guessIndex;
                if (guessType == GuessType.RANDOM)
                {
                    guessIndex = random.Next(statesCount);
                }
                else
                {
                    guessIndex = bestInitialGuess;
                }

                searchSpace.CopyTo(guessIndex, guess);

                int guessCount = 1;
                var feedback = Feedback(code, guess, colorCount);
                while (feedback.blackPegs != columns)
                {
                    if (logAmount == LogAmount.EACH_GUESS)
                    {
                        Console.WriteLine(string.Join(", ", guess.ToArray()));
                    }
                    Array.Fill(removeRows, false);

                    //Remove guess from search space
                    removeRows[guessIndex] = true;

                    //Mark invalid states
                    PruneSearchSpace(searchSpace, statesCount, removeRows, feedback, guess, columns, colorCount);

                    //Remove invalid states
                    statesCount = searchSpace.RemoveRows(removeRows, statesCount, columns);

                    //Make new guess
                    if (guessType == GuessType.RANDOM)
                    {
                        guessIndex = random.Next(statesCount);
                    }
                    else
                    {
                        guessIndex = BestGuess(searchSpace, removeRows, statesCount, columns, colorCount, guess, feedback);
                    }
                    searchSpace.CopyTo(guessIndex, guess);

                    feedback = Feedback(code, guess, colorCount);
                    guessCount++;
                }

                if (logAmount == LogAmount.EACH_GUESS)
                {
                    Console.WriteLine(string.Join(", ", guess.ToArray()));
                    Console.WriteLine($"Guesses: {guessCount}");
                }
                else if (logAmount == LogAmount.AFTER_EACH_GAME)
                {
                    Console.WriteLine($"Guesses: {guessCount}");
                }
                totalGuessCount += guessCount;
                maxGuesses = Math.Max(maxGuesses, guessCount);
            }
            watch.Stop();

            Console.WriteLine();
            Console.WriteLine($"Average guesses: {(totalGuessCount / (float)gamesToPlay).ToString("N2")}");
            Console.WriteLine($"Max: " + maxGuesses);
            Console.WriteLine($"Time: {(watch.ElapsedMilliseconds / 1000f).ToString("N2")}");
            Console.Read();
        }

        private enum GuessType
        {
            RANDOM,
            MINMAX
        }

        private enum LogAmount
        {
            ONLY_END,
            AFTER_EACH_GAME,
            EACH_GUESS
        }

        static void Main(string[] args)
        {
            //PlayGames(GuessType.MINMAX, 4, 6, 10_000, LogAmount.ONLY_END);
            //return;

            PrintHelp();

            while (true)
            {
                try
                {
                    string command = Console.ReadLine().Trim();
                    //Console.WriteLine(command);

                    if (command == "--help")
                    {
                        PrintHelp();
                    }

                    GuessType guessType = GuessType.RANDOM;
                    int columns = 4;
                    int colorCount = 6;
                    int gamesToRun = 1;
                    LogAmount logAmount = LogAmount.ONLY_END;

                    string[] splittedCommand = Regex.Replace(command, "[^a-zA-Z0-9-]", " ").Replace("  ", " ").Split(' ');

                    //No commands given
                    if (splittedCommand.Length == 0)
                    {
                        continue;
                    }

                    //First command has to specify the guess type
                    switch (splittedCommand[0])
                    {
                        case "random":
                        case "andom":
                            guessType = GuessType.RANDOM;
                            break;
                        case "minmax":
                        case "inmax":
                            guessType = GuessType.MINMAX;
                            break;
                        default:
                            Console.WriteLine("Invalid guess type. Has to be either random or minmax.");
                            CommandArguments["guessType"].Foreach(x => Console.WriteLine(x));
                            throw new CommandException();
                    }

                    string commandArgument = null;
                    if (TryGetCommandArgument(splittedCommand, ref commandArgument, "--columns"))
                    {
                        int number;
                        if (!int.TryParse(commandArgument, out number))
                        {
                            Console.WriteLine("Invalid command argument.");
                            CommandArguments["--columns"].Foreach(x => Console.WriteLine(x));
                            continue;
                        }
                        columns = number;
                    }
                    if (TryGetCommandArgument(splittedCommand, ref commandArgument, "--colors"))
                    {
                        int number;
                        if (!int.TryParse(commandArgument, out number))
                        {
                            Console.WriteLine("Invalid command argument.");
                            CommandArguments["--colors"].Foreach(x => Console.WriteLine(x));
                            continue;
                        }
                        colorCount = number;
                    }

                    if (TryGetCommandArgument(splittedCommand, ref commandArgument, "--games"))
                    {
                        int number;
                        if (!int.TryParse(commandArgument, out number))
                        {
                            Console.WriteLine("Invalid command argument.");
                            CommandArguments["--games"].Foreach(x => Console.WriteLine(x));
                            continue;
                        }
                        gamesToRun = number;
                    }
                    if (TryGetCommandArgument(splittedCommand, ref commandArgument, "--log"))
                    {
                        switch (commandArgument)
                        {
                            case "low":
                                logAmount = LogAmount.ONLY_END;
                                break;
                            case "med":
                                logAmount = LogAmount.AFTER_EACH_GAME;
                                break;
                            case "high":
                                logAmount = LogAmount.EACH_GUESS;
                                break;
                            default:
                                Console.WriteLine("Invalid command argument.");
                                CommandArguments["--log"].Foreach(x => Console.WriteLine(x));
                                break;
                        }
                    }

                    PlayGames(guessType, columns, colorCount, gamesToRun, logAmount);
                }
                catch (CommandException) { }
            }
        }

        private static bool TryGetCommandArgument(string[] commands, ref string commandArgument, string command)
        {
            for (int i = 0; i < commands.Length; i++)
            {
                if (commands[i] == command)
                {
                    if (i == commands.Length || commands[i + 1].StartsWith('-'))
                    {
                        Console.WriteLine($"The command {commands[i]} is missing an argument.");
                        CommandArguments[command].Foreach(x => Console.WriteLine(x));
                        throw new CommandException();
                    }
                    commandArgument = commands[i + 1];
                    return true;
                }
            }

            commandArgument = null;
            return false;
        }

        internal static Dictionary<string, string[]> CommandArguments = new Dictionary<string, string[]>()
        {
            { "guessType", new string[] 
            {
                "<guessType> commands:",
                "    random           Choses a random guess.",
                "    minmax           Uses minmax algorithm a guess.",
                ""
            } },
            { "--columns", new string[]
            {
                "<columnCount>        Number of columns in the game. Must be more than 0. Default is 4."
            } },
            { "--colors", new string[]
            {
                "<colorCount>         Number of colors in the game. Must be more than 1. Default is 6."
            } },
            { "--games", new string[]
            {
                "<gamesToRunCount>    Number of games to run. Default is 1."
            } },
            { "--log", new string[]
            {
                "<logAmount> commands:",
                "    low              Only prints out information after the games has run. This is the default option.",
                "    med              Prints out the number of gueeses in each game.",
                "    high             Prints out the code and each guess in each game.",
                ""
            } },
        };

        internal static void PrintHelp()
        {
            Console.WriteLine("<guessType> [--columns <columnCount>] [--colors <colorCount>] [--games <gamesToRunCount>] [--log <logAmount>]");
            CommandArguments["guessType"].Foreach(x => Console.WriteLine(x));
            CommandArguments["--columns"].Foreach(x => Console.WriteLine(x));
            CommandArguments["--colors"].Foreach(x => Console.WriteLine(x));
            CommandArguments["--games"].Foreach(x => Console.WriteLine(x));
            CommandArguments["--log"].Foreach(x => Console.WriteLine(x));
        }
    }

    internal class CommandException : Exception
    {
    }
}