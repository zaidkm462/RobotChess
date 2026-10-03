# References and Attribution

## Scientific and technical references

1. **SSIM**  
   Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). *Image quality assessment: From error visibility to structural similarity*. IEEE Transactions on Image Processing, 13(4), 600–612.  
   DOI: https://doi.org/10.1109/TIP.2003.819861  
   Used through `skimage.metrics.structural_similarity`.

2. **OpenCV perspective geometry**  
   The implementation uses OpenCV's `getPerspectiveTransform` and `warpPerspective` for a standard projective transform/homography.  
   Documentation: https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html

3. **Chess rules and legal move generation**  
   The project delegates chess rules and legal move generation to `python-chess`.  
   Documentation: https://python-chess.readthedocs.io/  
   Repository: https://github.com/niklasf/python-chess

4. **Stockfish**  
   Stockfish is an external UCI chess engine. Its search, NNUE evaluation, and implementation are not original algorithms of this project.  
   Website: https://stockfishchess.org/  
   Repository: https://github.com/official-stockfish/Stockfish  
   Local citation/license: `latest/stockfish/CITATION.cff` and `latest/stockfish/Copying.txt`

## Board-corner model

The optional corner detector referenced in the source is:

- **Model ID:** `chessboard-detection-yqcnu/3`
- **Roboflow model page:** https://universe.roboflow.com/chessboard-corner-detection-3b5bs/chessboard-detection-yqcnu
- **Version/dataset page:** https://universe.roboflow.com/chessboard-corner-detection-3b5bs/chessboard-detection-yqcnu/dataset/3

The model is an object detector trained for chessboard-corner annotations. The local code takes detections, converts their bounding-box centers into points, and orders the points. It is an optional fallback; calibrated `board_corners.json` is used when present. The model's accuracy has not been independently benchmarked in this repository.

## Local engineering contributions

The following are project-specific integration decisions, not claims of new scientific algorithms:

- Reusing calibrated corners instead of detecting them on every frame.
- Mapping 8×8 image cells to algebraic squares.
- Selecting changed squares from SSIM scores.
- Handling special castling patterns.
- Constraining observations to legal moves using symmetric differences.
- Translating UCI moves into calibrated pick/place/throw sequences.
- Verifying the robot move with a subsequent visual observation.
- Keeping camera and arm integration behind replaceable adapters.

## External hardware and services

- A phone/IP Camera application that provides an HTTP still-image endpoint.
- Arduino Uno and servo motors.
- Roboflow Inference/model endpoint for the optional corner detector.
- A compatible 6-DOF robotic arm; the project does not require a proprietary arm design.

## Suggested citation

```bibtex
@software{chess_robot_prototype,
  title  = {Vision-Guided Robotic Chessboard},
  author = {Project contributors},
  year   = {2026},
  note   = {Prototype integrating IP camera vision, python-chess, Stockfish, Arduino, and a 6-DOF robotic arm}
}
```
