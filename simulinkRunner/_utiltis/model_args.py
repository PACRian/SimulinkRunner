import json
from pathlib import Path
from itertools import product
from typing import Dict, List, Any, Iterator, Union


class GridArguments():
    """A class to manage and iterate over grid parameter combinations."""
    
    def __init__(self, params: Dict[str, Iterator]=None):
        """
        Initialize with a dictionary of parameters where each value is a list of options.
        
        Args:
            params (Dict[str, List[Any]]): Dictionary with parameter names as keys and lists of values as values.

        Example:
        Create a GridArguments instance with parameters in a dictionary:
        ```python
        params = {
            'learning_rate': [0.01, 0.1],
            'batch_size': [16, 32],
            'optimizer': ['adam', 'sgd']
        }
        grid = GridArguments(params)
        ```

        or load from a JSON file:
        ```python
        grid = GridArguments.from_json("grid_params.json")
        ```
        """
        self.params = params
        self.param_names = params.keys()
        
        self._combinations = self._generate_combinations(self.param_names, params.values())
        self._index = 0
        self._iterator = None

    @classmethod
    def from_json(cls, json_path: str) -> 'GridArguments':
        """
        Create a GridArguments instance from a JSON file.
        
        Args:
            json_path (str | Path): Path to the JSON file containing parameters.
        
        Returns:
            GridArguments: An instance initialized with JSON data.
        
        Raises:
            FileNotFoundError: If the JSON file doesn't exist.
            json.JSONDecodeError: If the JSON file is invalid.
            ValueError: If the JSON data doesn't match the expected format.

        Call this method to create a GridArguments instance from a JSON file like:
        ```
        GridArguments.from_json("grid_params.json")
        ```
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with json_path.open('r') as f:
            params = json.load(f)
        
        cls._validate_params(params)
        return cls(params)

    def _generate_combinations(self, names: Iterator, values: Iterator) -> List[Dict[str, Any]]:
        """Generate all possible combinations of parameters."""
        combinations = []

        # pv = [params[name] for name in self.param_names]
        for val in product(*values):
            combination = dict(zip(names, val))
            combinations.append(combination)
        return combinations
    
    def current(self) -> Dict[str, Any]:
        """Return the current combination."""
        return self._combinations[self._index-1]

    def __iter__(self) -> 'GridArguments':
        """Make the class iterable."""
        self._iterator = iter(self._combinations)
        return self

    def __next__(self) -> Dict[str, Any]:
        """Return the next combination."""
        if self._iterator is None:
            self._iterator = iter(self._combinations)
        
        self._index += 1
        return next(self._iterator)
    
    def __len__(self) -> int:
        return len(self._iterator)
    
    def keys(self) -> List[str]:
        """Return the parameter names."""
        return self.param_names
    
    def __getitem__(self, index: Union[int, str]) -> Dict[str, Any]:
        """
        Get a specific combination by index.
        
        Args:
            index (int): Index of the combination to retrieve.
        
        Returns:
            Dict[str, Any]: The combination at the specified index.
        
        Raises:
            IndexError: If index is out of range.
        """
        if isinstance(index, int) and 0 <= index < len(self._combinations):
            return self._combinations[index]
        elif isinstance(index, str) and index in self.param_names:
            return self.current()[index]
        raise IndexError(f"Index {index} out of range or not in the iterable scope.")
        
    def __str__(self) -> str:
        """String representation of the grid arguments."""
        return f"GridArguments with {self.totals()} combinations: {self.params}"
    
    def rewind(self):
        """Explicitly move the iterator to the beginning of the combinations."""
        self._iterator = iter(self._combinations)
        self._index = 0

    def totals(self) -> int:
        """Return the total number of combinations."""
        return len(self._combinations)


# Example usage
if __name__ == "__main__":
    # Define parameters
    params = {
        'learning_rate': [0.01, 0.1],
        'batch_size': [16, 32],
        'optimizer': ['adam', 'sgd']
    }

    # Create GridArguments instance
    grid = GridArguments(params)

    print(f"Grid object: {grid}")

    # Print total combinations
    print(f"Total combinations: {grid.totals()}")

    # Iterate over combinations
    print("\nIterating over all combinations:")
    for combo in grid:
        print(combo ,type(combo))
        print(f"grid['batch_size'] = {grid['batch_size']}")
        # for k, v in combo.items():
        #     print(f"{k}: {v}\t", end='\n')
            


    # Reset and get specific combination
    grid.rewind()
    print("\nCombination at index 2:", grid[2])

    # Use next() manually
    grid.rewind()
    print("\nUsing next():")
    print(next(grid))
    print(next(grid))
    print(grid)
    print(f"grid['batch_size'] = {grid['batch_size']}")
