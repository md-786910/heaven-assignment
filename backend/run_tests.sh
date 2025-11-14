#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q -r requirements.txt

echo -e "${YELLOW}Running all tests...${NC}"
python -m pytest tests/ -v

echo -e "\n${YELLOW}Running tests with coverage...${NC}"
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

echo -e "\n${GREEN}Test results summary:${NC}"
echo -e "Coverage report generated in: htmlcov/index.html"

echo -e "\n${YELLOW}Running specific test categories:${NC}"
echo -e "${GREEN}Authentication tests:${NC}"
python -m pytest tests/ -v -m auth

echo -e "\n${GREEN}Issue tests:${NC}"
python -m pytest tests/ -v -m issues

echo -e "\n${GREEN}Comment tests:${NC}"
python -m pytest tests/ -v -m comments

echo -e "\n${GREEN}All tests completed!${NC}"
