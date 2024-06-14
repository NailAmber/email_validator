# Email Validator

## Overview
This program validates email addresses by checking if they are accessible. The program currently uses SOCKS5 proxies and reads emails from a file named `emails.txt`. The results are then distributed into two files: one with valid emails and another with invalid emails, including the error messages explaining why the email could not be accessed.

## Instructions

1. **Setup**
    - Ensure that your proxy settings are configured for SOCKS5.

2. **Input File**
    - Place the email addresses you want to validate into a file named `emails.txt`.

3. **Run the Program**
    - Start the program to begin the validation process. The emails will be checked, and the results will be distributed into two files:
        - `good_emails`: This file will contain all the valid emails.
        - `bad_emails`: This file will contain all the invalid emails along with error messages explaining why each email could not be accessed.

## Development Status
The program is currently under development. New features and improvements are being added regularly. If you encounter any issues or have suggestions for enhancements, feel free to contribute or open an issue.

## Contributing
Contributions are welcome! If you have any ideas for new features or find any bugs, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.
