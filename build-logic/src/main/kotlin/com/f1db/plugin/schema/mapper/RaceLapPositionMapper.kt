package com.f1db.plugin.schema.mapper

import com.f1db.plugin.schema.single.LapPosition
import com.f1db.plugin.schema.single.Race
import org.mapstruct.AfterMapping
import org.mapstruct.Context
import org.mapstruct.Mapper
import org.mapstruct.Mapping
import org.mapstruct.MappingTarget
import com.f1db.plugin.schema.splitted.LapPosition as SplittedLapPosition

/**
 * The lap position mapper.
 */
@Mapper
interface RaceLapPositionMapper {

    @Mapping(target = "raceId", ignore = true)
    @Mapping(target = "year", ignore = true)
    @Mapping(target = "round", ignore = true)
    fun toSplittedLapPosition(lapPosition: LapPosition, @Context race: Race): SplittedLapPosition

    fun toSplittedLapPositions(lapPositions: List<LapPosition>, @Context race: Race): List<SplittedLapPosition>

    @AfterMapping
    fun afterMapping(@MappingTarget splittedLapPosition: SplittedLapPosition, @Context race: Race) {
        splittedLapPosition.raceId = race.id
        splittedLapPosition.year = race.year
        splittedLapPosition.round = race.round
    }
}
