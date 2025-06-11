#!/usr/bin/env python3
"""
General pattern validation utility for all log types in logtypes_events_timestamps.yaml.

This utility validates that:
1. All patterns have required fields
2. All patterns compile successfully 
3. Group numbers are valid for each pattern
4. Extracted timestamps can be parsed with their specified dateformat
5. Epoch patterns extract valid Unix timestamps
"""

import re
import unittest
import yaml
from datetime import datetime
from typing import Dict, Any, List


class TestAllLogTypePatterns(unittest.TestCase):
    """Test all log type patterns for configuration correctness."""
    
    @classmethod
    def setUpClass(cls):
        """Load the complete YAML configuration."""
        with open('logtypes_events_timestamps.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)
    
    def validate_pattern_syntax(self, log_type: str, pattern_config: Dict[str, Any]) -> None:
        """Validate that a pattern compiles successfully."""
        pattern_name = pattern_config['name']
        pattern_regex = pattern_config['pattern']
        
        try:
            re.compile(pattern_regex)
        except re.error as e:
            self.fail(f"{log_type}.{pattern_name}: Pattern failed to compile: {e}")
    
    def validate_required_fields(self, log_type: str, pattern_config: Dict[str, Any]) -> None:
        """Validate that a pattern has all required fields."""
        pattern_name = pattern_config['name']
        required_fields = ['name', 'pattern', 'group']
        
        for field in required_fields:
            self.assertIn(field, pattern_config, 
                        f"{log_type}.{pattern_name}: Missing required field '{field}'")
        
        # Validate group number
        group_num = pattern_config['group']
        self.assertIsInstance(group_num, int, 
                            f"{log_type}.{pattern_name}: 'group' must be integer, got {type(group_num)}")
        self.assertGreater(group_num, 0, 
                         f"{log_type}.{pattern_name}: 'group' must be positive, got {group_num}")
    
    def validate_group_count(self, log_type: str, pattern_config: Dict[str, Any]) -> None:
        """Validate that the group number doesn't exceed the number of capture groups."""
        pattern_name = pattern_config['name']
        pattern_regex = pattern_config['pattern']
        group_num = pattern_config['group']
        
        try:
            # Create a test regex to count groups
            regex = re.compile(pattern_regex)
            max_groups = regex.groups
            
            self.assertLessEqual(group_num, max_groups,
                               f"{log_type}.{pattern_name}: group {group_num} exceeds available groups ({max_groups})")
        except re.error:
            # Pattern syntax error will be caught by validate_pattern_syntax
            pass
    
    def validate_dateformat_compatibility(self, log_type: str, pattern_config: Dict[str, Any]) -> None:
        """Validate that dateformat and epoch settings are consistent."""
        pattern_name = pattern_config['name']
        is_epoch = pattern_config.get('epoch', False)
        dateformat = pattern_config.get('dateformat')
        
        if is_epoch:
            self.assertIsNone(dateformat, 
                            f"{log_type}.{pattern_name}: Epoch patterns should not have dateformat")
        else:
            self.assertIsNotNone(dateformat,
                               f"{log_type}.{pattern_name}: Non-epoch patterns must have dateformat")
            
            # Validate dateformat syntax
            if dateformat:
                try:
                    # Test with a known timestamp
                    test_time = datetime(2024, 1, 15, 9, 30, 45)
                    formatted = test_time.strftime(dateformat)
                    parsed = datetime.strptime(formatted, dateformat)
                    
                    # For syslog patterns without year, only compare the components that are included
                    if '%Y' not in dateformat:
                        # For syslog timestamps, just verify the format works
                        # and that the parsed components match (ignoring year)
                        self.assertEqual(test_time.month, parsed.month,
                                       f"{log_type}.{pattern_name}: month mismatch in dateformat '{dateformat}'")
                        self.assertEqual(test_time.day, parsed.day,
                                       f"{log_type}.{pattern_name}: day mismatch in dateformat '{dateformat}'")
                        self.assertEqual(test_time.hour, parsed.hour,
                                       f"{log_type}.{pattern_name}: hour mismatch in dateformat '{dateformat}'")
                        self.assertEqual(test_time.minute, parsed.minute,
                                       f"{log_type}.{pattern_name}: minute mismatch in dateformat '{dateformat}'")
                        self.assertEqual(test_time.second, parsed.second,
                                       f"{log_type}.{pattern_name}: second mismatch in dateformat '{dateformat}'")
                    else:
                        # For full timestamps with year, do complete round-trip validation
                        self.assertEqual(test_time.replace(microsecond=0), parsed.replace(microsecond=0),
                                       f"{log_type}.{pattern_name}: dateformat '{dateformat}' round-trip failed")
                except (ValueError, TypeError) as e:
                    self.fail(f"{log_type}.{pattern_name}: Invalid dateformat '{dateformat}': {e}")
    
    def test_all_patterns_basic_validation(self):
        """Run basic validation on all patterns in all log types."""
        for log_type, log_config in self.config.items():
            if 'timestamps' not in log_config:
                continue
                
            patterns = log_config['timestamps']
            
            for pattern_config in patterns:
                with self.subTest(log_type=log_type, pattern=pattern_config.get('name', 'unnamed')):
                    self.validate_required_fields(log_type, pattern_config)
                    self.validate_pattern_syntax(log_type, pattern_config)
                    self.validate_group_count(log_type, pattern_config)
                    self.validate_dateformat_compatibility(log_type, pattern_config)
    
    def test_base_time_patterns(self):
        """Ensure each log type has exactly one base_time pattern."""
        for log_type, log_config in self.config.items():
            if 'timestamps' not in log_config:
                continue
                
            patterns = log_config['timestamps']
            base_time_patterns = [p for p in patterns if p.get('base_time', False)]
            
            with self.subTest(log_type=log_type):
                self.assertEqual(len(base_time_patterns), 1, 
                               f"{log_type}: Should have exactly one base_time pattern, found {len(base_time_patterns)}")
    
    def test_pattern_names_unique(self):
        """Ensure pattern names within each log type are unique."""
        for log_type, log_config in self.config.items():
            if 'timestamps' not in log_config:
                continue
                
            patterns = log_config['timestamps']
            pattern_names = [p['name'] for p in patterns]
            unique_names = set(pattern_names)
            
            with self.subTest(log_type=log_type):
                self.assertEqual(len(pattern_names), len(unique_names),
                               f"{log_type}: Duplicate pattern names found: {pattern_names}")
    
    def validate_sample_data_if_available(self, log_type: str) -> bool:
        """Test patterns against sample data if available."""
        import os
        
        # Look for sample files
        sample_files = [f"{log_type}.log", f"{log_type}_demo.log", f"{log_type.lower()}.log"]
        sample_file = None
        
        for filename in sample_files:
            if os.path.exists(filename):
                sample_file = filename
                break
        
        if not sample_file:
            return False  # No sample data available
        
        log_config = self.config[log_type]
        patterns = log_config['timestamps']
        
        with open(sample_file, 'r') as f:
            sample_lines = f.readlines()
        
        for pattern_config in patterns:
            pattern_name = pattern_config['name']
            pattern_regex = pattern_config['pattern']
            group_num = pattern_config['group']
            is_epoch = pattern_config.get('epoch', False)
            dateformat = pattern_config.get('dateformat')
            
            try:
                regex = re.compile(pattern_regex)
                
                for line_num, line_text in enumerate(sample_lines, 1):
                    line_text = line_text.strip()
                    matches = list(regex.finditer(line_text))
                    
                    for match in matches:
                        if len(match.groups()) >= group_num:
                            timestamp_text = match.group(group_num)
                            
                            # Validate extracted timestamp
                            if is_epoch:
                                try:
                                    epoch_timestamp = int(timestamp_text)
                                    # Basic range check for Unix timestamps
                                    self.assertGreater(epoch_timestamp, 0)
                                    self.assertLess(epoch_timestamp, 4102444800)  # Year 2100
                                except ValueError:
                                    self.fail(f"{log_type}.{pattern_name}: Invalid epoch timestamp '{timestamp_text}' "
                                            f"from line {line_num}")
                            elif dateformat:
                                try:
                                    parsed_datetime = datetime.strptime(timestamp_text, dateformat)
                                    # For syslog patterns without year, skip year validation
                                    if '%Y' in dateformat:
                                        self.assertGreater(parsed_datetime.year, 1970)
                                        self.assertLess(parsed_datetime.year, 2100)
                                except ValueError as e:
                                    self.fail(f"{log_type}.{pattern_name}: Failed to parse '{timestamp_text}' "
                                            f"from line {line_num} with format '{dateformat}': {e}")
                            
            except re.error:
                # Pattern syntax errors already caught by other tests
                pass
        
        return True
    
    def test_patterns_with_sample_data(self):
        """Test patterns against available sample data."""
        tested_types = []
        skipped_types = []
        
        for log_type in self.config.keys():
            if 'timestamps' not in self.config[log_type]:
                continue
                
            with self.subTest(log_type=log_type):
                if self.validate_sample_data_if_available(log_type):
                    tested_types.append(log_type)
                else:
                    skipped_types.append(log_type)
        
        # Print summary
        if tested_types:
            print(f"\\nTested {len(tested_types)} log types with sample data: {', '.join(tested_types)}")
        if skipped_types:
            print(f"Skipped {len(skipped_types)} log types (no sample data): {', '.join(skipped_types[:5])}{'...' if len(skipped_types) > 5 else ''}")


if __name__ == '__main__':
    print("Validating all timestamp patterns in logtypes_events_timestamps.yaml...")
    print("=" * 80)
    unittest.main(verbosity=2)