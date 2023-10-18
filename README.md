# dinnerdate-public

DinnerDate is an open-source project designed to assist couples, groups, and individuals in making decisions on where to eat.

## Getting Started

To run the project in development mode, follow these steps:

### Prerequisites

Make sure you have Python and Django installed on your system.

### Installation

1. Clone this repository to your local machine.
2. Install all project dependencies.
3. Create a `keys.py` file in both the `dinnerdate/` and `dinnerpicker/` directories.
4. Inside the `keys.py` files, assign values for the required keys, and set the Django secret key with the appropriate names.

   Example:

   ```python
   # dinnerdate/keys.py
   django_key = "your_django_secret_key_here"
   ```

   ```python
   # dinnerpicker/keys.py
   yelp_key = "your_yelp_api_key_here"
   ```

5. Run the development server.

```bash
python manage.py runserver [IP:PORT]
```

6. Ensure that your `keys.py` files have the base URL and port for the development server.

### Notes

This is a public version of my own personal project. DinnerDate is for personal use ONLY.
