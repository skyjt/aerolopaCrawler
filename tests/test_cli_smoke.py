from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch
import sys

import aerolopa_crawler.cli as cli


def test_cli_main_smoke(tmp_path: Path, monkeypatch):
    """Test CLI main function with list-airlines command."""
    # Mock sys.argv to simulate command line arguments
    test_args = ["aerolopa-crawler", "--list-airlines"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Mock the list_supported_airlines function to avoid actual output
    with patch('aerolopa_crawler.cli.list_supported_airlines') as mock_list:
        mock_list.return_value = None
        
        # Call main function
        cli.main()
        
        # Verify the function was called
        mock_list.assert_called_once()


def test_cli_main_with_airline(tmp_path: Path, monkeypatch):
    """Test CLI main function with airline crawling."""
    outdir = tmp_path / "out"
    test_args = ["aerolopa-crawler", "--airline", "CA", "--output-dir", str(outdir), "-v"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Mock the AerolopaCrawler to avoid actual crawling
    with patch('aerolopa_crawler.cli.AerolopaCrawler') as mock_crawler_class:
        mock_crawler = Mock()
        mock_crawler.crawl_airline_seatmaps.return_value = 5
        mock_crawler.get_crawl_statistics.return_value = {"total_processed": 5}
        mock_crawler_class.return_value = mock_crawler
        
        # Mock config loading
        with patch('aerolopa_crawler.cli.load_config') as mock_config:
            mock_config_obj = Mock()
            mock_config_obj.crawler.output_dir = str(outdir)
            mock_config.return_value = mock_config_obj
            
            # Mock validate_airline_codes to return valid codes
            with patch('aerolopa_crawler.cli.validate_airline_codes') as mock_validate:
                mock_validate.return_value = ["CA"]
                
                # Call main function
                cli.main()
                
                # Verify crawler was called
                mock_crawler.crawl_airline_seatmaps.assert_called_once_with("CA")

