import subprocess
import os
import shutil # For removing directories
import tempfile # For creating temporary directories
import requests # For direct image downloads
from urllib.parse import urlparse

def download_media_from_url(url, download_base_dir, media_type, progress_callback=None):
    """
    Downloads media from a URL using yt-dlp or requests (for direct images).
    Downloads into a type-specific subfolder within the base download directory.

    Args:
        url (str): The URL of the media to download.
        download_base_dir (str): The base directory where the media will be downloaded (e.g., temp dir).
        media_type (str): The type of media ('image', 'video', 'audio') to create a subfolder.
        progress_callback (callable, optional): A function to call with progress updates.

    Returns:
        tuple: (bool, str) - True for success, False for failure, and the path to the downloaded file.
    """
    # Create type-specific subfolder within the base download directory
    download_dir = os.path.join(download_base_dir, media_type)
    if not os.path.isdir(download_dir):
        try:
            os.makedirs(download_dir)
            if progress_callback:
                progress_callback(f"Created download subfolder: {download_dir}")
        except OSError as e:
            return False, f"Error creating download directory '{download_dir}': {e}"

    # --- Determine if it's a direct image link or needs yt-dlp ---
    # Simple check for common image extensions in the URL path
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    parsed_url = urlparse(url)
    # Check if the URL path ends with a common image extension AND it's not a complex Google Images redirect
    if parsed_url.path.lower().endswith(image_extensions) and "google.com/url" not in url.lower():
        # It looks like a direct image link without complex redirect parameters
        if progress_callback:
            progress_callback(f"Attempting direct image download for: {url}...")
        return _download_direct_image(url, download_dir, progress_callback)
    else:
        # Assume it needs yt-dlp for video, audio, or complex image URLs (like from hosting sites)
        if progress_callback:
            progress_callback(f"Attempting yt-dlp download for: {url}...")
        return _download_via_yt_dlp(url, download_dir, media_type, progress_callback)


def _download_direct_image(url, download_dir, progress_callback):
    """
    Downloads an image directly using the requests library.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors

        # Infer filename from URL or use a generic one
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename or len(filename.split('.')[-1]) > 5: # If no filename, no extension, or extension too long
            # Try to get extension from content-type header
            content_type = response.headers.get('content-type', '')
            if 'image/jpeg' in content_type:
                ext = '.jpg'
            elif 'image/png' in content_type:
                ext = '.png'
            elif 'image/gif' in content_type:
                ext = '.gif'
            elif 'image/webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg' # Default fallback

            # Use a generic filename with inferred extension
            filename = f"downloaded_image_{os.urandom(4).hex()}{ext}" # Add random hex to avoid conflicts
        
        file_path = os.path.join(download_dir, filename)

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded_size += len(chunk)
                if progress_callback:
                    # Simulate yt-dlp progress dict for consistency
                    percent_str = f"{downloaded_size / total_size * 100:.1f}%" if total_size > 0 else "N/A%"
                    downloaded_bytes_str = f"{downloaded_size / (1024*1024):.2f} MiB" if downloaded_size > 0 else "0 MiB"
                    total_bytes_str = f"{total_size / (1024*1024):.2f} MiB" if total_size > 0 else "N/A MiB"

                    progress_callback({
                        'status': 'downloading',
                        'total_bytes': total_size,
                        'downloaded_bytes': downloaded_size,
                        '_percent_str': percent_str,
                        '_downloaded_bytes_str': downloaded_bytes_str,
                        '_total_bytes_str': total_bytes_str,
                        '_speed_str': 'N/A', # Requests doesn't provide speed easily
                        '_eta_str': 'N/A', # Requests doesn't provide ETA easily
                    })
        if progress_callback:
            progress_callback(f"Download successful: {file_path}")
        return True, file_path
    except requests.exceptions.RequestException as e:
        return False, f"Network error downloading image from {url}: {e}"
    except Exception as e:
        return False, f"Error downloading image from {url}: {e}"

def _download_via_yt_dlp(url, download_dir, media_type, progress_callback):
    """
    Downloads media using yt-dlp.
    """
    # yt-dlp command base
    # -o %(title)s.%(ext)s: Output filename template (saves with original title and extension)
    # --no-playlist: Don't download entire playlists
    # --restrict-filenames: Keep filenames simple
    # --no-warnings: Suppress warnings
    command = [
        'yt-dlp',
        url,
        '-o', os.path.join(download_dir, '%(title)s.%(ext)s'),
        '--no-playlist',
        '--restrict-filenames',
        '--no-warnings'
    ]

    # Add format selection based on media_type
    if media_type == 'video':
        # Prioritize best quality video+audio, prefer mp4/m4a
        command.extend(['--format', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'])
    elif media_type == 'audio':
        # Extract audio and convert to mp3 if possible, or just download best audio
        command.extend(['--extract-audio', '--audio-format', 'mp3', '--audio-quality', '0']) # 0 is best quality
    elif media_type == 'image':
        # For images, yt-dlp generally works for direct image links or image-hosting pages it recognizes.
        command.extend(['--format', 'best']) # Try to get the best available format

    try:
        if progress_callback:
            progress_callback(f"Attempting to download from URL: {url} using yt-dlp...")

        process = subprocess.run(command, check=True, capture_output=True, text=True)

        downloaded_file_path = None
        # Parse yt-dlp output to find the downloaded file path
        # Look for lines indicating "Destination:" or "Writing video to:"
        for line in process.stdout.splitlines() + process.stderr.splitlines():
            if "Destination:" in line:
                downloaded_file_path = line.split("Destination:")[1].strip()
                break
            elif "Writing video to:" in line:
                 downloaded_file_path = line.split("Writing video to:")[1].strip()
                 break
            elif "[ExtractAudio]" in line and "Destination:" in line:
                 downloaded_file_path = line.split("Destination:")[1].strip()
                 break
            elif "[ExtractVideo]" in line and "Destination:" in line:
                 downloaded_file_path = line.split("Destination:")[1].strip()
                 break

        if downloaded_file_path:
            # yt-dlp might output relative paths, make sure it's absolute
            if not os.path.isabs(downloaded_file_path):
                potential_path = os.path.join(download_dir, os.path.basename(downloaded_file_path))
                if os.path.exists(potential_path):
                    downloaded_file_path = potential_path
                else:
                    # Fallback: sometimes yt-dlp outputs full path directly
                    pass
            
            if os.path.exists(downloaded_file_path):
                if progress_callback:
                    progress_callback(f"Download successful: {downloaded_file_path}")
                return True, downloaded_file_path
            else:
                return False, f"Download completed, but could not verify downloaded file at path: {downloaded_file_path}. yt-dlp output:\n{process.stdout}\n{process.stderr}"
        else:
            return False, f"Could not determine downloaded file path from yt-dlp output. yt-dlp output:\n{process.stdout}\n{process.stderr}"

    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Error during download: yt-dlp exited with code {e.returncode}.\n"
            f"yt-dlp stdout:\n{e.stdout}\n"
            f"yt-dlp stderr:\n{e.stderr}\n"
            "Please check the URL and ensure yt-dlp is installed and accessible."
        )
        return False, error_msg
    except FileNotFoundError:
        return False, "Error: 'yt-dlp' command not found. Please ensure yt-dlp is installed and accessible in your system's PATH."
    except Exception as e:
        return False, f"An unexpected error occurred during download: {e}"


def convert_media(input_path, output_directory, output_format, progress_callback=None,
                  image_quality=None, scale_width=None, scale_height=None, scale_percentage=None,
                  video_quality_preset=None):
    """
    Core function to convert a media file using ffmpeg, with optional image/video adjustments.

    Args:
        input_path (str): The absolute or relative path to the input media file.
        output_directory (str): The directory where the converted file will be saved.
                                This directory must exist.
        output_format (str): The desired output format (e.g., 'mp4', 'png', 'mp3', 'gif').
        progress_callback (callable, optional): A function to call with progress updates.
        image_quality (int, optional): Quality for image output (1-100). Applies to JPG, WEBP.
        scale_width (int, optional): Desired output width in pixels.
        scale_height (int, optional): Desired output height in pixels.
        scale_percentage (float, optional): Scale factor as a percentage (e.g., 50.0 for 50%).
        video_quality_preset (str, optional): Preset for video quality (e.g., '1080p', '720p', '480p', 'best_crf', 'medium_crf').

    Returns:
        tuple: (bool, str) - True for success, False for failure, and a message.
    """
    # Ensure the output directory exists. If not, create it.
    if not os.path.isdir(output_directory):
        try:
            os.makedirs(output_directory)
            if progress_callback:
                progress_callback(f"Created output directory: {output_directory}")
        except OSError as e:
            return False, f"Error creating output directory '{output_directory}': {e}"

    # Extract the base name of the input file without its extension
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Construct the full path for the output file
    final_output_path = os.path.join(output_directory, f"{base_name}.{output_format}")

    # Start building the ffmpeg command
    command = ['ffmpeg', '-i', input_path]

    # --- Add image/video specific options ---
    filter_complex = []
    output_options = []

    # Scaling/Rescaling
    if scale_percentage is not None:
        # Scale by percentage. FFmpeg uses "scale=iw*percent/100:ih*percent/100"
        filter_complex.append(f"scale=iw*{scale_percentage/100}:ih*{scale_percentage/100}")
    elif scale_width is not None or scale_height is not None:
        # Scale by pixels. Use -1 for auto-scaling the other dimension
        width_arg = str(scale_width) if scale_width is not None else "-1"
        height_arg = str(scale_height) if scale_height is not None else "-1"
        filter_complex.append(f"scale={width_arg}:{height_arg}")

    # Image Quality (for formats that support it, like JPG, WEBP)
    if image_quality is not None and output_format.lower() in ['jpg', 'jpeg', 'webp']:
        # For JPG, -q:v (or -qscale:v) sets quality (2-31, lower is better, 2 is best).
        # For WEBP, -q:v sets quality (0-100, higher is better).
        # We'll map 1-100 to appropriate FFmpeg values.
        if output_format.lower() in ['jpg', 'jpeg']:
            # Invert quality for JPG: 100 (best) -> 2 (FFmpeg), 1 (worst) -> 31 (FFmpeg)
            ffmpeg_quality = 2 + ((100 - image_quality) / 100) * 29
            output_options.extend(['-q:v', str(int(ffmpeg_quality))])
        elif output_format.lower() == 'webp':
            output_options.extend(['-q:v', str(image_quality)])

    # Video Quality Presets
    if video_quality_preset:
        if video_quality_preset == '1080p':
            filter_complex.append("scale=1920:1080")
            output_options.extend(['-crf', '23', '-preset', 'medium']) # Good balance
        elif video_quality_preset == '720p':
            filter_complex.append("scale=1280:720")
            output_options.extend(['-crf', '23', '-preset', 'medium'])
        elif video_quality_preset == '480p':
            filter_complex.append("scale=854:480") # Standard 16:9 480p
            output_options.extend(['-crf', '23', '-preset', 'medium'])
        elif video_quality_preset == 'best_crf':
            output_options.extend(['-crf', '18', '-preset', 'veryfast']) # Visually lossless, fast encode
        elif video_quality_preset == 'medium_crf':
            output_options.extend(['-crf', '23', '-preset', 'medium']) # Good quality, reasonable speed
        elif video_quality_preset == 'low_crf':
            output_options.extend(['-crf', '28', '-preset', 'slow']) # Smaller file, slower encode, more compression

    # Apply filter_complex if any filters were added
    if filter_complex:
        command.extend(['-vf', ','.join(filter_complex)])

    # Add other output options
    command.extend(output_options)

    # Finally, add the output file path
    command.append(final_output_path)

    try:
        if progress_callback:
            progress_callback(f"Attempting to convert '{input_path}' to '{final_output_path}'...")
            progress_callback(f"FFmpeg command: {' '.join(command)}") # For debugging

        process = subprocess.run(command, check=True, capture_output=True, text=True)

        if progress_callback:
            progress_callback("Conversion successful!")
        return True, final_output_path

    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Error during conversion: FFmpeg exited with code {e.returncode}.\n"
            f"FFmpeg stdout:\n{e.stdout}\n"
            f"FFmpeg stderr:\n{e.stderr}\n"
            "Please check the input file, output format, and FFmpeg's error messages."
        )
        return False, error_msg
    except FileNotFoundError:
        return False, "Error: 'ffmpeg' command not found. Please ensure FFmpeg is installed and accessible in your system's PATH."
    except Exception as e:
        return False, f"An unexpected error occurred during conversion: {e}"

