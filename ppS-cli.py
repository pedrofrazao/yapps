#!/usr/bin/env python3
import sys
import os
from random import randint
import curses
import json
import multiprocessing

dirname = os.path.dirname(__file__)
sys.path.append(dirname)

from ppSlib.arena_sync_model import ArenaSyncModel
from ppSlib.agent import Agent, Block, LivingAgent, Grass
import ppSlib.agent as agent
import datetime
import argparse
from ppSlib.yml_loader import YMLArenaLoader

rows=16
cols=16


def load_from_file(args, **kwargs):
    if args.file:
        return YMLArenaLoader.load_arena_from_yml(args.file, kwarena=kwargs )


def _load_demo_grass():
    # Initialize the arena and objects
    arena = ArenaSyncModel(16, 16, sync_model='Sync')
    num_grass = 8
    num_cows = 4
    num_wolves = 1

    nearby = []
    for i in range(num_grass):
        obj = Grass(state_args={'age': randint(0, 9), 'min_matetime': 10, 'energy': 1}, priority=1, arena=arena)
        if len(nearby) > 0:
            x, y = nearby.pop()
            arena.add_to_position(x, y, obj)
        else:
            arena.add_to_random_position(obj)
            nearby = obj.see().find_empty_position()

    for i in range(num_cows):
        obj = agent.Cow(arena=arena, state_args={'energy': 45}, priority=10)
        arena.add_to_random_position(obj)

    # for i in range(num_wolves):
    #     obj = agent.Wolf(arena=arena, state_args={ 'energy':45}, priority=20)
    #     arena.add_to_random_position(obj)

    return arena


def _load_demo_arena(_):
    return _load_demo_grass()

    # Initialize the arena and objects
    arena = ArenaSyncModel(rows, cols, sync_model='Sync')
    num_traps = 5
    num_prey = 10
    num_predators = 2

    blocks = [Block(arena=arena) for i in range(int(cols * 3 / 4))]
    br = int(rows / 2)
    bc = randint(1, cols - 1)
    for b in blocks:
        arena.add_to_position(br, bc, b)
        bc += 1
        bc = bc % cols

    traps = [Trap(arena=arena) for i in range(num_traps)]
    for t in traps:
        arena.add_to_random_position(t)

    for i in range(num_prey):
        energy = randint(20, 40)
        obj = Prey(state_args={'energy': energy}, arena=arena)
        arena.add_to_random_position(obj)

    for i in range(num_predators):
        energy = randint(20, 40)
        obj = Carnivore(state_args={'energy': energy}, arena=arena, see_length=3)
        arena.add_to_random_position(obj)

    return arena


def load_args():
    parser = argparse.ArgumentParser(description='Matrix CLI')
    parser.add_argument('-f', '--file', type=str, help='File to load the arena from')
    parser.add_argument('--epochs', type=int, help='Number of epochs to run', default=100)
    parser.add_argument('--runs', type=int, help='Number of times to run the simulation (batch mode only)', default=1)
    parser.add_argument('--slow', action='store_true', help='Run the simulation slowly', default=False)
    parser.add_argument('--interactive', action='store_true', help='Run the simulation interactively', default=False)
    parser.add_argument('--batch', action='store_true', help='run without output', default=True)
    parser.add_argument('--parallel', type=int, help='Number of concurrent processes to run simulations', default=1)
    parser.add_argument('--progress', action='store_true', help='Show simulation execution progress', default=False)
    # parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    if args.interactive is True or args.slow is True:
        args.batch = False
        # Multiple runs only work in batch mode
        if args.runs > 1:
            print("Note: Multiple runs only available in batch mode. Setting runs to 1.")
            args.runs = 1
        # Parallel execution not available in interactive mode
        if args.parallel > 1:
            print("Note: Parallel execution not available in interactive mode. Setting parallel to 1.")
            args.parallel = 1

    return args


def generate_output_filename(input_file, run_number):
    """Generate an output filename based on input file and run number."""
    if input_file is None:
        # No input file specified, use a default name with timestamp
        now = datetime.datetime.now()
        return f"output-{now.strftime('%Y%m%d%H%M%S')}-run-{run_number}.csv"

    # Parse the input file path
    input_path = os.path.abspath(input_file)
    input_dir = os.path.dirname(input_path)
    input_name = os.path.splitext(os.path.basename(input_path))[0]

    # Create output filename
    return os.path.join(input_dir, f"{input_name}-run-{run_number}.csv")


def run_single_simulation(args, run_number):
    """Run a single simulation for parallel processing."""
    # Generate output filename
    output_file = generate_output_filename(args.file, run_number)
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load arena
    arena = load_from_file(args)
    if arena is None:
        arena = _load_demo_arena(args)
    
    # Run the simulation
    loop(None, arena, args.epochs, args)
    
    # Write results to output file
    with open(output_file, 'w') as f:
        # Write the final arena state
        f.write(str(arena) + "\n\n")
        
        # Write the stats
        for i in arena.get_stats():
            if i is not None:
                stat_line = ",".join([str(v) for v in i])
                f.write(stat_line + "\n")
    
    return run_number


def main_interactive(stdscr, args):
    for run in range(args.runs):
        stdscr.clear()
        stdscr.addstr(0, 0, f"Run {run + 1}/{args.runs}" if args.runs > 1 else "")

        arena = load_from_file(args)
        if arena is None:
            # load default
            arena = _load_demo_arena(args)

        # Display the arena
        stdscr.addstr(1, 0, str(arena))
        stdscr.addstr(rows + 3, 0, "====")

        # Run the loop with curses
        loop(stdscr, arena, args.epochs, args)

    height, width = stdscr.getmaxyx()
    stdscr.addstr(height - 1, 0, "Press 'q' to exit.")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('s'):
            now = datetime.datetime.now()
            filename = f"arena-{now.strftime('%Y%m%d%H%M%S')}.txt"
            with open(filename, 'w') as f:
                json.dump(arena.serialize(), f, indent=4)

            stdscr.addstr(height - 2, 0, f"Arena saved to {filename}")
            stdscr.refresh()


def main_batch(args):
    # Parallel processing for multiple runs
    if args.parallel > 1 and args.runs > 1:
        print(f"Running {args.runs} simulations with {args.parallel} parallel processes...")
        
        # Create a pool of worker processes
        pool = multiprocessing.Pool(processes=min(args.parallel, args.runs))
        
        # Track progress
        completed = 0
        
        # Define callback function for progress tracking
        def update_progress(_):
            nonlocal completed
            completed += 1
            if args.progress:
                print(f"\rCompleted {completed}/{args.runs} simulations ({completed/args.runs*100:.1f}%)", end="", flush=True)
        
        # Submit all tasks to the pool
        results = []
        for run in range(args.runs):
            run_number = run + 1
            result = pool.apply_async(
                run_single_simulation, 
                args=(args, run_number),
                callback=update_progress if args.progress else None
            )
            results.append(result)
        
        # Wait for all tasks to complete
        for result in results:
            result.wait()
        
        if args.progress:
            print()  # Add newline after progress display
        
        # Clean up the pool
        pool.close()
        pool.join()
        
    else:
        # Original sequential code
        for run in range(args.runs):
            run_number = run + 1
            
            # Generate output filename
            output_file = generate_output_filename(args.file, run_number)

            # Ensure directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            if args.progress and args.runs > 1:
                print(f"\rRun {run_number}/{args.runs} ({run_number/args.runs*100:.1f}%)", end="", flush=True)
            elif args.runs == 1:
                print(f"\n--- Starting run --- Output: {output_file} ---\n")

            f = open(output_file, 'w')
            def _write_stats(f,i):
                if i is not None:
                    stat_line = ",".join([str(v) for v in i])
                    f.write(stat_line + "\n")

            arena = load_from_file(args, dump_stats=lambda x: _write_stats(f,x))
            if arena is None:
                # load default
                arena = _load_demo_arena(args)

            if args.runs == 1:
                print(arena)

            # Run the loop without curses
            loop(None, arena, args.epochs, args)

            if args.runs == 1:
                print(arena)

            # Write results to output file
            # with open(output_file, 'w') as f:
            #     # Write the final arena state
            #     f.write(str(arena) + "\n\n")

            #     # Write the stats
            #     for i in arena.get_stats():
            #         if i is not None:
            #             stat_line = ",".join([str(v) for v in i])
            #             f.write(stat_line + "\n")
            #             if args.runs == 1:
            #                 print(",".join([str(v) for v in i]))
        
        if args.progress and args.runs > 1:
            print()  # Add newline after progress display


def main(stdscr, args):
    if stdscr is not None:
        main_interactive(stdscr, args)
    else:
        main_batch(args)


def loop(stdscr, arena, steps=5, args=None):
    if stdscr is not None:
        ## init stdscr
        num_rows, num_cols = stdscr.getmaxyx()
        lwin = curses.newpad(num_rows * 10, 255)
        c = None

    for i in range(steps):
        # Run a step in the arena
        msg = []
        arena.run_step()
        for obj in sorted(arena.get_objects(), key=lambda x: x.nickname):
            if isinstance(obj, LivingAgent):
                # msg.extend( [ f"{obj.nickname}-{m}" for m in obj.msg[-2:]] )
                msg.extend([f"{obj.nickname}-{obj.info()}"])

        if stdscr is not None:
            to_cont = stdscr_step(arena, stdscr, lwin, num_rows, num_cols, msg, args)
            if to_cont is False:
                break
        else:
            if i % (steps / 5) == 0 and (not hasattr(args, 'runs') or args.runs == 1):
                # Print the arena and messages only if runs = 1
                print(arena)


def stdscr_step(arena, stdscr, lwin, num_rows, num_cols, msg, args):
    # Clear the screen
    stdscr.clear()
    lwin.clear()

    # Display the arena
    stdscr.addstr(0, 0, str(arena))
    stdscr.addstr(rows + 2, 0, "====")

    for m in msg:
        lwin.addstr(f"{m}\n")
    # Refresh the screen to show the updated arena
    stdscr.refresh()
    # lwin.refresh(0,0, rows+3, 0, num_rows-(rows+2)-1, num_cols-1 )
    lwin.refresh(0, 0, rows + 3, 0, num_rows - 1, num_cols - 1)

    # Wait for a short period to create a visual effect
    if args.interactive is False:
        if args.slow:
            stdscr.timeout(1000)
            c = stdscr.getch()
            if c == -1:
                return True
            elif c == ord('q'):
                return False
        return True

    if c is not None and c == ord('q'):
        return False
    elif c is not None and c == ord('c'):
        stdscr.timeout(100)  # Set timeout for getch to 100 milliseconds
        c = stdscr.getch()
    else:
        stdscr.timeout(80000000)
        c = stdscr.getch()


if __name__ == "__main__":
    args = load_args()
    if args.batch is False:
        curses.wrapper(main, args)
    else:
        main(None, args)


