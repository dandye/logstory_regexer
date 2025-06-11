#!/usr/bin/env python3
"""
Unit tests for WINDOWS_SYSMON timestamp pattern matching.

Tests the simplified regex patterns that use optional matching for quotes and spaces
to ensure they correctly match all timestamp variations without duplicates.
"""

import re
import unittest
import yaml
from typing import List, Dict, Any
from datetime import datetime


class TestWindowsSysmonTimestamps(unittest.TestCase):
    """Test cases for WINDOWS_SYSMON timestamp pattern matching."""
    
    @classmethod
    def setUpClass(cls):
        """Load the YAML configuration and extract WINDOWS_SYSMON patterns."""
        with open('logtypes_events_timestamps.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
        
        cls.sysmon_patterns = cls.config['WINDOWS_SYSMON']['timestamps']
        
        # Load sample log data
        with open('WINDOWS_SYSMON.log', 'r') as f:
            cls.sample_lines = f.readlines()
    
    def apply_regex_patterns(self, text: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simplified version of the apply_regex_patterns function for testing.
        
        Args:
            text: The log line text to analyze
            patterns: List of pattern dictionaries from YAML config
            
        Returns:
            List of match dictionaries with position and group data
        """
        matches = []
        
        for idx, pattern_config in enumerate(patterns):
            pattern_name = pattern_config.get('name', f'Pattern {idx + 1}')
            pattern_regex = pattern_config.get('pattern', '')
            
            try:
                regex = re.compile(pattern_regex)
                for match in regex.finditer(text):
                    match_data = {
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group(0),
                        'pattern_name': pattern_name,
                        'pattern_index': idx,
                        'groups': []
                    }
                    
                    # Collect capture groups
                    for g_idx in range(1, len(match.groups()) + 1):
                        group = match.group(g_idx)
                        if group is not None:
                            match_data['groups'].append({
                                'index': g_idx,
                                'text': group,
                                'start': match.start(g_idx),
                                'end': match.end(g_idx)
                            })
                    
                    matches.append(match_data)
                    
            except re.error as e:
                print(f"Regex error in pattern '{pattern_name}': {e}")
                continue
        
        return matches
    
    def test_utc_time_pattern_variations(self):
        """Test UtcTime pattern matches all quoted and unquoted variations."""
        utc_time_pattern = next(p for p in self.sysmon_patterns if p['name'] == 'UtcTime')
        
        test_cases = [
            # JSON format variations
            '{"UtcTime": "2024-01-15 09:30:45"}',
            '{"UtcTime":"2024-01-15 09:30:45"}', 
            '{"UtcTime" : "2024-01-15 09:30:45"}',
            '{"UtcTime" :"2024-01-15 09:30:45"}',
            '{"UtcTime": 2024-01-15 09:30:45}',  # No quotes around value
            '{"UtcTime":2024-01-15 09:30:45}',
            
            # Syslog format variations
            'UtcTime: 2024-01-15 09:31:23',
            'UtcTime:2024-01-15 09:31:23',
            'UtcTime : 2024-01-15 09:31:23',
        ]
        
        regex = re.compile(utc_time_pattern['pattern'])
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                matches = list(regex.finditer(test_case))
                self.assertEqual(len(matches), 1, f"Should match exactly once: {test_case}")
                
                match = matches[0]
                # Verify the timestamp is captured in group 2
                timestamp = match.group(2)
                self.assertEqual(timestamp, "2024-01-15 09:30:45" if "09:30:45" in test_case else "2024-01-15 09:31:23")
    
    def test_creation_utc_time_pattern_variations(self):
        """Test CreationUtcTime pattern matches all quoted and unquoted variations."""
        creation_pattern = next(p for p in self.sysmon_patterns if p['name'] == 'CreationUtcTime')
        
        test_cases = [
            # JSON format variations
            '"CreationUtcTime": "2024-01-15 09:31:44"',
            '"CreationUtcTime":"2024-01-15 09:31:44"',
            '"CreationUtcTime" : "2024-01-15 09:31:44"',
            '"CreationUtcTime" :"2024-01-15 09:31:44"',
            '"CreationUtcTime": 2024-01-15 09:31:44',  # No quotes around value
            
            # Syslog format variations
            'CreationUtcTime: 2024-01-15 09:33:12',
            'CreationUtcTime:2024-01-15 09:33:12',
            'CreationUtcTime : 2024-01-15 09:33:12',
        ]
        
        regex = re.compile(creation_pattern['pattern'])
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                matches = list(regex.finditer(test_case))
                self.assertEqual(len(matches), 1, f"Should match exactly once: {test_case}")
                
                match = matches[0]
                # Verify the timestamp is captured in group 2
                timestamp = match.group(2)
                expected_timestamp = "2024-01-15 09:31:44" if "09:31:44" in test_case else "2024-01-15 09:33:12"
                self.assertEqual(timestamp, expected_timestamp)
    
    def test_sample_log_lines(self):
        """Test patterns against actual sample log data."""
        expected_matches = {
            # Line 1: JSON with UtcTime
            1: [('UtcTime', '2024-01-15 09:30:45'), ('EventTime', '1705312245'), ('EventReceivedTime', '1705312246')],
            
            # Line 2: JSON with UtcTime
            2: [('UtcTime', '2024-01-15 09:31:07'), ('EventTime', '1705312267'), ('EventReceivedTime', '1705312268')],
            
            # Line 3: Syslog with UtcTime
            3: [('syslog_timestamp', 'Jan 15 09:31:23'), ('UtcTime', '2024-01-15 09:31:23')],
            
            # Line 4: JSON with UtcTime and CreationUtcTime
            4: [('UtcTime', '2024-01-15 09:31:45'), ('EventTimeUTC', '2024-01-15 09:31:45'), 
                ('EventReceivedTimeUTC', '2024-01-15 09:31:46'), ('CreationUtcTime', '2024-01-15 09:31:44')],
            
            # Line 8: Syslog CreationUtcTime only
            8: [('CreationUtcTime', '2024-01-15 09:33:12')],
            
            # Line 10: Syslog with both UtcTime and CreationUtcTime
            10: [('syslog_timestamp', 'Jan 15 09:34:18'), ('UtcTime', '2024-01-15 09:34:18'), 
                 ('CreationUtcTime', '2024-01-15 09:34:17')],
        }
        
        for line_num, expected in expected_matches.items():
            with self.subTest(line_number=line_num):
                line_text = self.sample_lines[line_num - 1].strip()  # Convert to 0-based indexing
                matches = self.apply_regex_patterns(line_text, self.sysmon_patterns)
                
                # Extract pattern names and captured timestamps
                actual_matches = []
                for match in matches:
                    pattern_name = match['pattern_name']
                    # Find the timestamp group based on pattern configuration
                    pattern_config = next(p for p in self.sysmon_patterns if p['name'] == pattern_name)
                    group_num = pattern_config.get('group', 2)
                    
                    if len(match['groups']) >= group_num:
                        timestamp = match['groups'][group_num - 1]['text']  # Convert to 0-based indexing
                        actual_matches.append((pattern_name, timestamp))
                
                # Sort both lists for comparison
                expected_sorted = sorted(expected)
                actual_sorted = sorted(actual_matches)
                
                self.assertEqual(actual_sorted, expected_sorted, 
                               f"Line {line_num}: Expected {expected_sorted}, got {actual_sorted}")
    
    def test_no_duplicate_matches(self):
        """Ensure no single timestamp is matched by multiple patterns."""
        for line_num, line_text in enumerate(self.sample_lines, 1):
            line_text = line_text.strip()
            with self.subTest(line_number=line_num):
                matches = self.apply_regex_patterns(line_text, self.sysmon_patterns)
                
                # Collect all matched timestamp positions
                timestamp_positions = []
                for match in matches:
                    pattern_config = next(p for p in self.sysmon_patterns if p['name'] == match['pattern_name'])
                    group_num = pattern_config.get('group', 2)
                    
                    if len(match['groups']) >= group_num:
                        group = match['groups'][group_num - 1]
                        timestamp_positions.append((group['start'], group['end'], group['text']))
                
                # Check for overlapping positions (indicating duplicate matches)
                for i, (start1, end1, text1) in enumerate(timestamp_positions):
                    for j, (start2, end2, text2) in enumerate(timestamp_positions):
                        if i != j:
                            # Check if positions overlap
                            if not (end1 <= start2 or end2 <= start1):
                                self.fail(f"Line {line_num}: Overlapping timestamp matches found: "
                                        f"'{text1}' at {start1}-{end1} and '{text2}' at {start2}-{end2}")
    
    def test_pattern_syntax_validity(self):
        """Verify all patterns compile successfully."""
        for pattern_config in self.sysmon_patterns:
            pattern_name = pattern_config['name']
            pattern_regex = pattern_config['pattern']
            
            with self.subTest(pattern_name=pattern_name):
                try:
                    re.compile(pattern_regex)
                except re.error as e:
                    self.fail(f"Pattern '{pattern_name}' failed to compile: {e}")
    
    def test_base_time_pattern_exists(self):
        """Ensure there's exactly one base_time pattern."""
        base_time_patterns = [p for p in self.sysmon_patterns if p.get('base_time', False)]
        self.assertEqual(len(base_time_patterns), 1, "Should have exactly one base_time pattern")
        self.assertEqual(base_time_patterns[0]['name'], 'UtcTime', "UtcTime should be the base_time pattern")
    
    def test_required_pattern_fields(self):
        """Verify all patterns have required fields."""
        required_fields = ['name', 'pattern', 'group']
        
        for pattern_config in self.sysmon_patterns:
            pattern_name = pattern_config['name']
            
            with self.subTest(pattern_name=pattern_name):
                for field in required_fields:
                    self.assertIn(field, pattern_config, 
                                f"Pattern '{pattern_name}' missing required field '{field}'")
                
                # Verify group number is valid
                group_num = pattern_config['group']
                self.assertIsInstance(group_num, int, f"Pattern '{pattern_name}' group must be integer")
                self.assertGreater(group_num, 0, f"Pattern '{pattern_name}' group must be positive")
    
    def test_group_extracts_parseable_timestamp(self):
        """Verify that the specified group extracts a timestamp that can be parsed with the dateformat."""
        for pattern_config in self.sysmon_patterns:
            pattern_name = pattern_config['name']
            pattern_regex = pattern_config['pattern']
            group_num = pattern_config['group']
            is_epoch = pattern_config.get('epoch', False)
            dateformat = pattern_config.get('dateformat')
            
            # Skip patterns without dateformat (epoch-only patterns)
            if is_epoch or not dateformat:
                continue
                
            with self.subTest(pattern_name=pattern_name):
                regex = re.compile(pattern_regex)
                found_valid_match = False
                
                # Test against sample log lines
                for line_num, line_text in enumerate(self.sample_lines, 1):
                    line_text = line_text.strip()
                    matches = list(regex.finditer(line_text))
                    
                    for match in matches:
                        if len(match.groups()) >= group_num:
                            timestamp_text = match.group(group_num)
                            
                            # Try to parse the timestamp with the specified format
                            try:
                                parsed_datetime = datetime.strptime(timestamp_text, dateformat)
                                found_valid_match = True
                                
                                # Special case for syslog timestamps which don't include year
                                if pattern_name == 'syslog_timestamp' and '%Y' not in dateformat:
                                    # For syslog timestamps, just verify the month/day/time components are reasonable
                                    self.assertIn(parsed_datetime.month, range(1, 13), 
                                                f"Pattern '{pattern_name}' extracted invalid month from '{timestamp_text}'")
                                    self.assertIn(parsed_datetime.day, range(1, 32),
                                                f"Pattern '{pattern_name}' extracted invalid day from '{timestamp_text}'")
                                    self.assertIn(parsed_datetime.hour, range(0, 24),
                                                f"Pattern '{pattern_name}' extracted invalid hour from '{timestamp_text}'")
                                    self.assertIn(parsed_datetime.minute, range(0, 60),
                                                f"Pattern '{pattern_name}' extracted invalid minute from '{timestamp_text}'")
                                    self.assertIn(parsed_datetime.second, range(0, 60),
                                                f"Pattern '{pattern_name}' extracted invalid second from '{timestamp_text}'")
                                else:
                                    # For full timestamps, verify the year is reasonable
                                    self.assertGreater(parsed_datetime.year, 1970, 
                                                     f"Pattern '{pattern_name}' extracted timestamp '{timestamp_text}' "
                                                     f"from line {line_num} parsed to unrealistic year {parsed_datetime.year}")
                                    self.assertLess(parsed_datetime.year, 2100,
                                                   f"Pattern '{pattern_name}' extracted timestamp '{timestamp_text}' "
                                                   f"from line {line_num} parsed to unrealistic year {parsed_datetime.year}")
                            except ValueError as e:
                                self.fail(f"Pattern '{pattern_name}' group {group_num} extracted '{timestamp_text}' "
                                        f"from line {line_num} but failed to parse with format '{dateformat}': {e}")
                
                # Ensure we found at least one valid match to test the parsing
                if not found_valid_match:
                    # This might be OK for some patterns that don't appear in our sample data
                    print(f"Warning: Pattern '{pattern_name}' had no matches in sample data to test parsing")
    
    def test_epoch_patterns_extract_valid_timestamps(self):
        """Verify that epoch patterns extract valid Unix timestamps."""
        for pattern_config in self.sysmon_patterns:
            pattern_name = pattern_config['name']
            pattern_regex = pattern_config['pattern']
            group_num = pattern_config['group']
            is_epoch = pattern_config.get('epoch', False)
            
            # Only test epoch patterns
            if not is_epoch:
                continue
                
            with self.subTest(pattern_name=pattern_name):
                regex = re.compile(pattern_regex)
                found_valid_match = False
                
                # Test against sample log lines
                for line_num, line_text in enumerate(self.sample_lines, 1):
                    line_text = line_text.strip()
                    matches = list(regex.finditer(line_text))
                    
                    for match in matches:
                        if len(match.groups()) >= group_num:
                            timestamp_text = match.group(group_num)
                            
                            # Verify it's a valid integer
                            try:
                                epoch_timestamp = int(timestamp_text)
                                found_valid_match = True
                                
                                # Verify it's a reasonable Unix timestamp
                                # Should be between 1970-01-01 (0) and 2100-01-01 (4102444800)
                                self.assertGreater(epoch_timestamp, 0,
                                                 f"Pattern '{pattern_name}' extracted epoch '{timestamp_text}' "
                                                 f"from line {line_num} but it's not positive")
                                self.assertLess(epoch_timestamp, 4102444800,
                                               f"Pattern '{pattern_name}' extracted epoch '{timestamp_text}' "
                                               f"from line {line_num} but it's unrealistically large")
                                
                                # Convert to datetime for additional validation
                                parsed_datetime = datetime.fromtimestamp(epoch_timestamp)
                                self.assertGreater(parsed_datetime.year, 1970)
                                self.assertLess(parsed_datetime.year, 2100)
                                
                            except ValueError as e:
                                self.fail(f"Pattern '{pattern_name}' group {group_num} extracted '{timestamp_text}' "
                                        f"from line {line_num} but it's not a valid integer: {e}")
                            except (OSError, OverflowError) as e:
                                self.fail(f"Pattern '{pattern_name}' group {group_num} extracted '{timestamp_text}' "
                                        f"from line {line_num} but it's not a valid Unix timestamp: {e}")
                
                # Ensure we found at least one valid match to test
                if not found_valid_match:
                    print(f"Warning: Epoch pattern '{pattern_name}' had no matches in sample data to test")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)